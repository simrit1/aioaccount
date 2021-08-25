Intro
=====
This is a simple introduction for using aioaccount.

.. note::  All of the examples should be done within context of the event loop.

User ID format
--------------
User IDs are UUID4 without the '-', this is a 32 characters long string.

Basics
------
.. code-block:: python

    from aioaccount import AccountHandler

    handler = AccountHandler(
        engine=...
    )

    # Opens required sessions needed to function
    # Should only be called once
    await handler.start()

    # Closes opened sessions
    # Should only be called once
    await handler.close()


Engine types
------------
.. code-block:: python

    from aioaccount import AccountHandler, MongoEngine, SQLEngine, Database

    # Using Mongodb
    handler = AccountHandler(
        engine=MongoEngine(
            host="localhost",
            port=27017,
            database="aioaccount"
        )
    )

    # Using postgresql, mysql & sqlite
    # https://www.encode.io/databases/connections_and_transactions/#connection-options

    ## SQLite
    handler = AccountHandler(
        engine=SQLEngine(Database(
            "sqlite:///example.db"
        ))
    )

    ## Postgresql
    handler = AccountHandler(
        engine=SQLEngine(Database(
            "postgresql://localhost/example"
        ))
    )

    ## MySQL
    handler = AccountHandler(
        engine=SQLEngine(Database(
            "mysql://localhost/"
        ))
    )

Password Policy
---------------
.. code-block:: python

    from aioaccount import AccountHandler, PasswordPolicy

    handler = AccountHandler(
        engine=...,
        password_policy=PasswordPolicy(
            length=8,
            uppercase=2,
            numbers=2,
            special=2,
            nonletters=2
        )
    )

SMTP Client
-----------
.. code-block:: python

    from aioaccount import AccountHandler, SmtpClient, SmtpHtml

    # Plain text emails
    handler = AccountHandler(
        engine=...,
        smtp=SmtpClient(
            host="localhost",
            port=25,
            email="no-reply@example.com"
        ).confirm_layout(
            url="https://example.com/confirm?code={validation_code}",
            subject="Please confirm your email for Aioaccount example!",
            raw="""Thanks for signing up for Aioaccount example,
            please follow the link below to complete your login.

            {link}
            """
        ).reset_layout(
            url="https://example.com/reset?code={validation_code}",
            subject="Password reset request from Aioaccount",
            raw="""A password reset has been requested, if it wasn't you ignore this email,
            please follow the link below to reset your password.

            {link}
            """
        )
    )

    # HTML emails
    ## Uses jinja2 templating!
    handler = AccountHandler(
        engine=...,
        smtp=SmtpClient(
            host="localhost",
            port=25,
            email="no-reply@example.com"
        ).confirm_layout(
            url="https://example.com/confirm?code={validation_code}",
            subject="Please confirm your email for Aioaccount example!",
            html=SmtpHtml(
                path="./templates/email",
                file="confirm.html",
                url_key="url"
            )
        ).reset_layout(
            url="https://example.com/reset?code={validation_code}",
            subject="Password reset request from Aioaccount",
            html=SmtpHtml(
                path="./templates/email",
                file="reset.html",
                url_key="url"
            )
        )
    )
