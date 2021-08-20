from dataclasses import dataclass, fields
from typing import Union


@dataclass
class UserModel(init=False):
    """Holds details on a user.
    """

    user_id: str
    name: Union[None, str] = None
    email: Union[None, str] = None
    email_confirmed: Union[None, bool] = None

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)
