import aiosmtplib

from email.mime.text import MIMEText
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape


class SmtpHtml:
    def __init__(self, path: str, file: str,
                 url_key: str = "url") -> None:
        """Configure SMTP html template

        Parameters
        ----------
        path : str
            Path to jinja2 templates.
        file : str
            Name of jinja2 template.
        url_key : str, optional
            Key for validation email url,
            by default "url"
        """

        self._jinja2 = Environment(
            loader=FileSystemLoader(path),
            autoescape=select_autoescape(["html", "xml"])
        )

        self._file = file
        self._url_key = url_key


class SmtpClient:
    def __init__(self, host: str, port: int,
                 url: str, email: str, subject: str,
                 html: SmtpHtml = None,
                 raw: str =
                 "Please confirm your email\n{validation_link}",
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
        email : str
            Email address to send as.
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

        self._email = email
        self._subject = subject

        self._html = html

    async def _send(self, email: str, code: str) -> None:
        """Used to send a email.

        Parameters
        ----------
        email : str
        code : str
        """

        if self._url_contains_placement:
            link = self._url.format(validation_code=code)
        else:
            link = self._url + code

        if self._html:
            message = MIMEText(self._html._jinja2.get_template(
                self._html._file
            ).render({self._html._url_key: link}), "html", "utf-8")
        else:
            message = EmailMessage()

            if self._raw_contains_placement:
                content = self._raw.format(validation_link=link)
            else:
                content = self._raw + link

            message.set_content(content)

        message["From"] = self._email
        message["To"] = email
        message["Subject"] = self._subject

        async with self._client:
            await self._client.send_message(message)
