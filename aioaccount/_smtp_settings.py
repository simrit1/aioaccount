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
                 **kwargs) -> None:
        """Used to configure SMTP.

        Parameters
        ----------
        host : str
        port : int
        url : str
            Url user follows for validation
            If it doesn't contain '{validation_code}'
            the validation code will be append
            to the end of the url

            e.g.
            https://example.com/validate?code={validation_code}
        html: SmtpHtml, optional
            by default None

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
        self._contains_placement = "{validation_code}" in self._url
        self._html = html
