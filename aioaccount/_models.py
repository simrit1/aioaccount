from dataclasses import dataclass
from typing import Union


@dataclass
class UserModel:
    """Holds details on a user.
    """

    user_id: str
    name: Union[None, str] = None
    email: Union[None, str] = None
    email_confirmed: Union[None, bool] = None
