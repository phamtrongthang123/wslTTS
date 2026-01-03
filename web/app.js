const form = document.getElementById("tts-form");
const textArea = document.getElementById("text");
const voiceInput = document.getElementById("voice");
const voiceList = document.getElementById("voice-list");
const voiceHint = document.getElementById("voice-hint");
const langSelect = document.getElementById("lang");
const speedInput = document.getElementById("speed");
const speedValue = document.getElementById("speed-value");
const statusEl = document.getElementById("status");
const audioEl = document.getElementById("audio");
const downloadEl = document.getElementById("download");
const durationEl = document.getElementById("duration");
const sampleButton = document.getElementById("sample");
const speakButton = document.getElementById("speak");

const sampleText =
  "Kokoro is a lightweight text to speech model. It sounds natural, runs fast, and stays entirely on your server.";

let voicesById = {};
let currentUrl = null;

function setStatus(message, tone = "") {
  statusEl.textContent = message;
  statusEl.className = tone ? tone : "";
}

function setBusy(isBusy) {
  speakButton.disabled = isBusy;
  sampleButton.disabled = isBusy;
}

function updateSpeedLabel() {
  const value = Number.parseFloat(speedInput.value || "1");
  speedValue.textContent = `${value.toFixed(2)}x`;
}

function updateVoiceHint() {
  const voice = voiceInput.value.trim();
  const info = voicesById[voice];
  if (info) {
    voiceHint.textContent = `${info.language} (${info.lang_code})`;
  } else if (voice) {
    voiceHint.textContent = "Unknown voice. Set language if needed.";
  } else {
    voiceHint.textContent = "Select a voice to begin.";
  }
}

function populateVoiceList(voices, defaultVoice) {
  voiceList.innerHTML = "";
  voices.forEach((voice) => {
    const option = document.createElement("option");
    option.value = voice.id;
    option.label = `${voice.language} (${voice.lang_code})`;
    voiceList.appendChild(option);
  });
  voiceInput.value = defaultVoice || voiceInput.value;
  updateVoiceHint();
}

function populateLanguages(languages) {
  const existing = new Set([""]); // keep Auto
  languages
    .slice()
    .sort((a, b) => a.language.localeCompare(b.language))
    .forEach((lang) => {
      if (existing.has(lang.lang_code)) {
        return;
      }
      const option = document.createElement("option");
      option.value = lang.lang_code;
      option.textContent = `${lang.language} (${lang.lang_code})`;
      langSelect.appendChild(option);
      existing.add(lang.lang_code);
    });
}

async function loadVoices() {
  try {
    const response = await fetch("/api/voices");
    if (!response.ok) {
      throw new Error("Failed to load voices");
    }
    const data = await response.json();
    voicesById = Object.fromEntries(data.voices.map((voice) => [voice.id, voice]));
    populateVoiceList(data.voices, data.default_voice);
    populateLanguages(data.languages);
    setStatus("Ready.", "ok");
  } catch (error) {
    setStatus("Could not load voices. Check the server.", "error");
    voiceHint.textContent = "Unable to load voice list.";
  }
}

async function submitForm(event) {
  event.preventDefault();
  const text = textArea.value.trim();
  const voice = voiceInput.value.trim();
  const speed = Number.parseFloat(speedInput.value || "1");

  if (!text) {
    setStatus("Enter some text.", "error");
    return;
  }
  if (!voice) {
    setStatus("Select a voice.", "error");
    return;
  }

  const payload = { text, voice, speed };
  if (langSelect.value) {
    payload.lang_code = langSelect.value;
  }

  setBusy(true);
  setStatus("Generating audio...", "");
  downloadEl.classList.add("disabled");
  durationEl.textContent = "";

  try {
    const response = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || "Request failed";
      throw new Error(message);
    }

    const blob = await response.blob();
    if (currentUrl) {
      URL.revokeObjectURL(currentUrl);
    }
    currentUrl = URL.createObjectURL(blob);
    audioEl.src = currentUrl;
    downloadEl.href = currentUrl;
    downloadEl.classList.remove("disabled");

    const duration = response.headers.get("X-Duration-Seconds");
    durationEl.textContent = duration ? `Duration: ${duration}s` : "";

    await audioEl.play();
    setStatus("Audio ready.", "ok");
  } catch (error) {
    setStatus(error.message || "Something went wrong.", "error");
  } finally {
    setBusy(false);
  }
}

speedInput.addEventListener("input", updateSpeedLabel);
voiceInput.addEventListener("input", updateVoiceHint);
sampleButton.addEventListener("click", () => {
  textArea.value = sampleText;
  textArea.focus();
});
form.addEventListener("submit", submitForm);

updateSpeedLabel();
loadVoices();
