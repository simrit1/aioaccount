import aiojobs

from typing import Union
from databases import Database
from motor.motor_asyncio import AsyncIOMotorClient
from password_strength import PasswordPolicy as ExtPP

from ._engines import SQLEngine, MongoEngine
from ._smtp_settings import SmtpClient
from ._pass_policy import PasswordPolicy

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
    "PasswordPolicy"
]


class AccountHandler:
    _smtp: Union[SmtpClient, None]
    _db: Union[Database, AsyncIOMotorClient]
    _jobs: Union[aiojobs.Scheduler, None]
    _policy: Union[ExtPP, None]

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
        else:
            self._db = AsyncIOMotorClient(
                engine._connection
            )

        self._smtp = smtp
        self._policy = password_policy._policy

    async def start(self) -> None:
        """Opens needed sessions.
        """

        if isinstance(self._db, Database):
            await self._db.connect()

        if self._smtp:
            self._jobs = await aiojobs.create_scheduler()
        else:
            self._jobs = None

    async def close(self) -> None:
        """Closes any closed sessions.
        """

        if isinstance(self._db, Database):
            await self._db.disconnect()

        if self._jobs:
            await self._jobs.close()
