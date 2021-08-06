import aiojobs

from typing import Union
from databases import Database
from secrets import token_urlsafe
from motor.motor_asyncio import AsyncIOMotorClient
from password_strength import PasswordPolicy as ExtPP
from email_validator import validate_email, EmailNotValidError
from bcrypt import hashpw, gensalt

from ._engines import SQLEngine, MongoEngine
from ._smtp_settings import SmtpClient
from ._pass_policy import PasswordPolicy
from ._sql import create_tables, SqlWrapper
from ._mongo import MongoWrapper
from ._errors import (
    AioAccountError,
    AccountDetailsError,
    EmailError,
    DetailsExistError,
    PasswordPolicyError,
    AccountNameTooLong
)
from ._util import generate_id
from ._models import UserModel

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
    "AccountNameTooLong"
]


class AccountHandler:
    _smtp: Union[SmtpClient, None]
    _db: Union[Database, AsyncIOMotorClient]
    _jobs: aiojobs.Scheduler
    _policy: ExtPP
    _db_wrapper: Union[SqlWrapper, MongoWrapper]

    __MAX_NAME_LEN = 128

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

    async def create_account(self, name: str, password: str,
                             email: str = None) -> UserModel:
        """Used to create a user account.

        Parameters
        ----------
        name : str
            Unique name of user, max length 128
        password : str
            Password of user
        email : str, optional
            by default None

        Returns
        -------
        UserModel

        Raises
        ------
        DetailsExistError
            Raised when user with given details already exists.
        EmailError
            Raised when email is invalid.
        PasswordPolicyError
            Raised when password doesn't meet password policy
        AccountNameTooLong
            Raised when name over 128 chars.
        """

        if len(name) > self.__MAX_NAME_LEN:
            raise AccountNameTooLong(
                f"Name is over {self.__MAX_NAME_LEN} characters."
            )

        results = self._policy.test(password)
        if results:
            raise PasswordPolicyError(results)

        values = {
            "user_id": generate_id(),
            "name": name
        }

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
                values["email_vaildate"] = token_urlsafe(32)

                # send email
                await self._jobs.spawn()
        else:
            if await self._db_wrapper.exists("user", values):
                raise DetailsExistError()

        values["password"] = hashpw(  # type: ignore
            password.encode(), gensalt()
        )

        await self._db_wrapper.insert("user", values)

        return user_modal
