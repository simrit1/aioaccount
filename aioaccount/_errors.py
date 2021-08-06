class AioAccountError(Exception):
    def __init__(self, msg: str, *args: object) -> None:
        super().__init__(msg, *args)


class AccountDetailsError(AioAccountError):
    pass


class EmailError(AccountDetailsError):
    pass


class AccountNameTooLong(AccountDetailsError):
    pass


class DetailsExistError(AccountDetailsError):
    def __init__(self, msg: str = "Account details already used.",
                 *args: object) -> None:
        super().__init__(msg, *args)


class PasswordPolicyError(AccountDetailsError):
    def __init__(self, failed: list,
                 msg: str = "Password doesn't meet password policy.",
                 *args: object) -> None:
        self.failed = failed
        super().__init__(msg, *args)
