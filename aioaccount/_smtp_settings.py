from typing import Union
import aiosmtplib


class SmtpHtml:
    def __init__(self, path: str,
                 url_key: str = "url") -> None:
        """Configure SMTP html template

        Parameters
        ----------
        path : str
            Path to jinja2 template.
        url_key : str, optional
            Key for validation email url,
            by default "url"
        """

        self._path = path
        self._url_key = url_key


class SmtpClient:
    def __init__(self, host: str, port: int,
                 url: str, html: SmtpHtml = None,
                 raw: Union[str, None] =
                 "Please confirm your email\n{validation_link}",
                 **kwargs) -> None:
        """Used to configure SMTP.

        Parameters
        ----------
        host : str
        port : int{validation_link}
        url : str
            Url user follows for validation
            If it doesn't contain '{validation_code}'
            the validation code will be append
            to the end of the url

            e.g.
            https://example.com/validate?code={validation_code}
        html: SmtpHtml, optional
            by default None
        raw : str, optional
            Should contain 'validation_link' otherwise
            appended at the end of the string.
            by default 'Please confirm your email\n{validation_link}'

        Notes
        -----
        Kwargs are passed to aiosmtplib's
        SMTP client.

        https://aiosmtplib.readthedocs.io/en/stable/client.html
        """

        self._client = aiosmtplib.SMTP(
            hostname=host,
            port=port,
            **kwargs
        )

        self._url = url
        self._url_contains_placement = "{validation_code}" in self._url

        self._raw = raw
        self._raw_contains_placement = (
            "{validation_link}" in self._raw
            if self._raw else False
        )

        self._html = html
