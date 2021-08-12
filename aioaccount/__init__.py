import aiojobs

from typing import Tuple, Union
from databases import Database
from secrets import token_urlsafe
from motor.motor_asyncio import AsyncIOMotorClient
from password_strength import PasswordPolicy as ExtPP
from email_validator import validate_email, EmailNotValidError
from bcrypt import hashpw, gensalt, checkpw

from ._engines import SQLEngine, MongoEngine
from ._smtp import SmtpClient
from ._pass_policy import PasswordPolicy
from ._sql import create_tables, SqlWrapper
from ._mongo import MongoWrapper
from ._errors import (
    AioAccountError,
    AccountDetailsError,
    EmailError,
    DetailsExistError,
    PasswordPolicyError,
    AccountNameTooLong,
    InvalidLogin,
    UnableToConfirmEmail
)
from ._util import generate_id
from ._models import UserModel
from ._user import User
from ._const import _MAX_NAME_LEN

__version__ = "0.0.0"
__url__ = "https://aioaccount.readthedocs.io/en/latest/"
__description__ = "Utility for user account creation, modification & email confirmation."  # noqa: E501
__author__ = "WardPearce"
__author_email__ = "wardpearce@protonmail.com"
__license__ = " AGPL-3.0"


__all__ = [
    "Database",
    "AccountHandler",
    "SQLEngine",
    "MongoEngine",
    "SmtpClient",
    "PasswordPolicy",
    "AioAccountError",
    "AccountDetailsError",
    "EmailError",
    "DetailsExistError",
    "UserModel",
    "PasswordPolicyError",
    "AccountNameTooLong",
    "UnableToConfirmEmail"
]


class AccountHandler:
    _smtp: Union[SmtpClient, None]
    _db: Union[Database, AsyncIOMotorClient]
    _jobs: aiojobs.Scheduler
    _policy: ExtPP
    _db_wrapper: Union[SqlWrapper, MongoWrapper]

    def __init__(self, engine: Union[MongoEngine, SQLEngine],
                 password_policy: PasswordPolicy = PasswordPolicy(),
                 smtp: SmtpClient = None,
                 ) -> None:
        """Configure how the account handler works.

        Parameters
        ----------
        engine : Union[MongoEngine, SQLEngine]
            Engine for storing accounts.
        password_policy : PasswordPolicy, optional
            Password policies, by default PasswordPolicy()
        smtp : SmtpClient, optional
            Smtp client for email validation, by default None
        """

        if isinstance(engine, SQLEngine):
            self._db = engine._connection
            self._db_wrapper = SqlWrapper(self._db)

            create_tables(str(engine._connection.url))
        else:
            self._db = AsyncIOMotorClient(
                engine._connection
            )[engine._database]
            self._db_wrapper = MongoWrapper(self._db)

        self._smtp = smtp
        self._policy = password_policy._policy

    async def start(self) -> None:
        """Opens needed sessions.
        """

        if isinstance(self._db, Database):
            await self._db.connect()

        self._jobs = await aiojobs.create_scheduler()

    async def close(self) -> None:
        """Closes any closed sessions.
        """

        if isinstance(self._db, Database):
            await self._db.disconnect()

        await self._jobs.close()

    def user(self, user_id: str) -> User:
        """Used to interact with user.

        Parameters
        ----------
        user_id : str

        Returns
        -------
        User
        """

        return User(self, user_id)

    def _validate_details(self, name: str = None,
                          password: str = None) -> None:
        """Used to validate details.

        Parameters
        ----------
        name : str, optional
        password : str, optional

        Raises
        ------
        AccountNameTooLong
        PasswordPolicyError
        """

        if name and len(name) > _MAX_NAME_LEN:
            raise AccountNameTooLong(
                f"Name is over {_MAX_NAME_LEN} characters."
            )

        if password:
            results = self._policy.test(password)
            if results:
                raise PasswordPolicyError(results)

    async def login(self, password: str, name: str = None,
                    email: str = None) -> Tuple[UserModel, User]:
        """Used to validate user's login.

        Parameters
        ----------
        password : str
        name : str, optional
            by default None
        email : str, optional
            by default None

        Returns
        -------
        UserModel
            Holds info on user.
        User
            Used to interact with user.

        Raises
        ------
        InvalidLogin
            Raised when user login is invalid.
        """

        assert not name or not email, "Email or name is required."

        if name:
            search = {
                "name": name
            }
        else:
            search = {
                "email": email
            }

        row = await self._db_wrapper.get("user", search)
        if not row:
            raise InvalidLogin()

        if not checkpw(password.encode(), row["password"]):
            raise InvalidLogin()

        return UserModel(**row), self.user(row["user_id"])

    def _email_regenerate(self) -> dict:
        return {
            "email_vaildate": token_urlsafe(32),
            "email_confirmed": False
        }

    async def confirm_email(self, email: str, given_code: str) -> User:
        """Used to confirm email from given code.

        Parameters
        ----------
        email : str
            User's email
        given_code : str
            Code the user provided.

        Returns
        -------
        User

        Raises
        ------
        UnableToConfirmEmail
        """

        result = await self._db_wrapper.get("user", {"email": email})
        if not result:
            raise UnableToConfirmEmail()

        # Midigates timing attacks.
        valid = checkpw(
            given_code.encode(), hashpw(
                result["email_vaildate"].encode(),
                gensalt()
            )
        )
        if not valid:
            raise UnableToConfirmEmail()

        await self._db_wrapper.update(
            "user",
            {"user_id": result["user_id"]},
            {
                "email_vaildate": None,
                "email_confirmed": True
            }
        )

        return self.user(result["user_id"])

    async def to_user(self, email: str = None, name: str = None) -> User:
        """Used to convert email or user to user object.

        Parameters
        ----------
        email : str, optional
            by default None
        name : str, optional
            by default None

        Returns
        -------
        User

        Raises
        ------
        AccountDetailsError
        """

        values = {}
        if email:
            values["email"] = email
        elif name:
            values["user"] = name
        else:
            raise AccountDetailsError("User or email must be provided.")

        result = await self._db_wrapper.get("user", values)
        if not result:
            raise AccountDetailsError("No user found with those details.")

        return self.user(result["user_id"])

    async def create_account(self, password: str,
                             email: str = None, name: str = None
                             ) -> Tuple[UserModel, User]:
        """Used to create a user account.

        Parameters
        ----------
        name : str, optional
            Unique name of user, max length 128
        password : str
            Password of user
        email : str, optional
            by default None

        Returns
        -------
        UserModel
            Holds info on user.
        User
            Used to interact with user.

        Raises
        ------
        DetailsExistError
            Raised when user with given details already exists.
        EmailError
            Raised when email is invalid.
        PasswordPolicyError
            Raised when password doesn't meet password policy
        AccountNameTooLong
            Raised when name over 128 characters.
        """

        assert not name or not email, "Email or name is required."

        self._validate_details(name, password)

        values = {
            "user_id": generate_id()
        }

        if name:
            values["name"] = name

        user_modal = UserModel(**values)

        if email:
            try:
                valid = validate_email(email)
            except EmailNotValidError as error:
                raise EmailError(str(error))

            values["email"] = valid.email

            if await self._db_wrapper.exists("user", values):
                raise DetailsExistError()

            user_modal.email = values["email"]

            if self._smtp:
                user_modal.email_confirmed = False
                values = {
                    **values,
                    **self._email_regenerate()
                }

                await self._jobs.spawn(
                    self._smtp._send(
                        values["email"],
                        values["email_vaildate"]
                    )
                )
        else:
            if await self._db_wrapper.exists("user", values):
                raise DetailsExistError()

        values["password"] = hashpw(  # type: ignore
            password.encode(), gensalt()
        )

        await self._db_wrapper.insert("user", values)

        return user_modal, self.user(values["user_id"])
