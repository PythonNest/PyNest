from typing import Any


class BaseProvider:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass
