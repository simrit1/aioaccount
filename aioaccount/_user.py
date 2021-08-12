from typing import Mapping, Optional, TYPE_CHECKING
from bcrypt import checkpw, hashpw, gensalt

from ._models import UserModel
from ._errors import InvalidUserId, InvalidLogin


if TYPE_CHECKING:
    from . import AccountHandler


class User:
    def __init__(self, upper: "AccountHandler", user_id: str) -> None:
        self._upper = upper
        self.user_id = user_id

    @property
    def __and(self) -> dict:
        return {"user_id": self.user_id}

    async def __raw_user(self) -> Optional[Mapping]:
        return await self._upper._db_wrapper.get(
            "user", self.__and
        )

    async def update_password(self, current_password: str,
                              new_password: str) -> None:
        """Used to update the password if they already know
           there current password.

        Parameters
        ----------
        current_password : str
        new_password : str

        Raises
        ------
        InvalidLogin
        """

        user = await self.__raw_user()
        if not user:
            raise InvalidLogin()

        if not checkpw(current_password.encode(), user["password"]):
            raise InvalidLogin()

        self._upper._validate_details(password=new_password)

        await self._upper._db_wrapper.update(
            "user", self.__and, {
                "password": hashpw(new_password.encode(), gensalt())
            }
        )

    async def update_email(self, new_email) -> None:
        pass

    async def reset_password(self) -> None:
        pass

    async def get(self) -> UserModel:
        """Used to get details on user.

        Returns
        -------
        UserModel

        Raises
        ------
        InvalidUserId
        """

        result = await self.__raw_user()
        if not result:
            raise InvalidUserId()

        return UserModel(**result)
