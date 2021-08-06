from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from . import AccountHandler


class User:
    def __init__(self, upper: "AccountHandler", user_id: str) -> None:
        self._upper = upper
        self.user_id = user_id
