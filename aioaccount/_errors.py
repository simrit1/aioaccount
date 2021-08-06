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
    def __init__(self, *args: object) -> None:
        super().__init__("Account details already used.", *args)


class PasswordPolicyError(AccountDetailsError):
    def __init__(self, fails: list, *args: object) -> None:
        self.fails = fails
        super().__init__("Password doesn't meet password policy.", *args)


class InvalidLogin(AioAccountError):
    def __init__(self, *args: object) -> None:
        super().__init__("Provided details are incorrect.", *args)
