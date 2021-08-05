from password_strength import PasswordPolicy as ExtPP


class PasswordPolicy:
    def __init__(self, length: int = 8,
                 uppercase: int = 2,
                 numbers: int = 2,
                 special: int = 2,
                 nonletters: int = 2,
                 strength: float = 0.66) -> None:
        """Used to set password policy.

        Parameters
        ----------
        length : int, optional
            Min char length, by default 8
        uppercase : int, optional
            Min amount of uppercase chars required,
            by default 2
        numbers : int, optional
            Min amount of numbers required, by default 2
        special : int, optional
            Min amount of special chars required,
            by default 2
        nonletters : int, optional
            Min number of non letter characters,
            by default 2
        strength : float, optional
            Required strength of password
            by default 0.66
        """

        self._policy = ExtPP.from_names(
            length=length,
            uppercase=uppercase,
            numbers=numbers,
            special=special,
            nonletters=nonletters,
            strength=strength
        )
