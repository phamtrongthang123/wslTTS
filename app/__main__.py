from __future__ import annotations

import uvicorn

from .config import SERVER_HOST, SERVER_PORT


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
