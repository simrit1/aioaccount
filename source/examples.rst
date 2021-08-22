Examples
========
Currently working on a starlette web app example!

.. note::
    For all the examples below, assume 'handler' is a initialized instance of 'AccountHandler'
    and ran within the context of the event loop.

Creating accounts
-----------------
.. note::
    If SMTP details given, if a email is provided
    users will be sent a email getting them to confirm there email.

.. code-block:: python

    # Email only
    model, user = await handler.create_account(
        password="some password what passes the policy",
        email="example@protonmail.com"
    )

    # Name only
    model, user = await handler.create_account(
        password="some password what passes the policy",
        name="ward42"
    )

    # Both
    model, user = await handler.create_account(
        password="some password what passes the policy",
        name="ward42",
        email="example@protonmail.com"
    )

Logging in
----------
.. code-block:: python

    from aioaccount import InvalidLogin

    try:
        await handler.login(
            # Provide a email or name
            email=None, name=None,
            password="1234",
            # If true, smtp provided & email provided by user
            # Email confirmation required to login
            require_email_confirmed=True
        )
    except InvalidLogin:
        print("Password, email or name incorrect")
    else:
        print("I've logged in!")

Confirm email
-------------
.. code-block:: python

    from aioaccount import UnableToConfirmEmail

    try:
        await handler.confirm_email(
            email="example@protonmail.com",
            given_code="some long code aioaccount generated"
        )
    except UnableToConfirmEmail:
        print("Invalid code or email")
    else:
        print("Email confirmed!")

Converting a name or email to user ID
-------------------------------------
.. note::
    Ideally you should be storing user IDs in your own database once generated,
    but if you ever need to convert a name or email to a user ID you can.

    The issue with relying on 'to_user' is that if a user changes name or email
    and someone as starts using that name or email, you'll be doing actions
    on a different user then you except. Ideally always use user IDs.

.. code-block:: python

    # Email
    model, user = await handler.to_user(
        email="example@protonmail.com"
    )

    # Name
    model, user = await handler.to_user(
        name="ward42"
    )


Listing users
-------------
.. code-block:: python

    async for model, user in handler.users():
        print(model.name)


Interacting with a user
-----------------------
.. note::
    Assume all references to 'user' are the initialized instance of 'User'

Getting a user object from a user ID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    user = handler.user(
        user_id="123"
    )

Updating password
^^^^^^^^^^^^^^^^^
.. code-block:: python

    from aioaccount import InvalidLogin, PasswordPolicyError

    try:
        await user.update_password(
            current_password="current password",
            new_password="new password"
        )
    except InvalidLogin:
        print("Current password incorrect")
    except PasswordPolicyError:
        print("Password doesn't meet our password policy")
    else:
        print("Password updated!")

Updating name
^^^^^^^^^^^^^
.. code-block:: python

    from aioaccount import DetailsExistError, NameLengthInvalidError, NameInvalidCharactersError

    try:
        await user.update_name(
            name="ward43"
        )
    except DetailsExistError:
        print("Sorry that name is taken.")
    except NameLengthInvalidError:
        print("Sorry that name is too long")
    except NameInvalidCharactersError:
        print("Sorry that name contains illegal characters")
    else:
        print("Name updated")

Updating email
^^^^^^^^^^^^^^
.. note::
    If SMTP client provided, users will be required to confirm there email again.

.. code-block:: python

    from aioaccount import EmailError, DetailsExistError

    try:
        await user.update_email(
            new_email="exam@protonmail.com"
        )
    except EmailError:
        print("Email is invalid")
    except DetailsExistError:
        print("Email already exist")
    else:
        print("Email updated")

Reset password
^^^^^^^^^^^^^^
.. note::
    If SMTP client provided, users will be required to confirm password reset from email.

.. code-block:: python

    # 'reset_password' will return the generated reset code,
    # this should only be used if SMTP isn't being used or a email isn't provided.
    code = await user.reset_password()


Confirm password reset
^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from aioaccount import PasswordResetInvalid, PasswordPolicyError

    try:
        await user.password_confirm(
            new_password="123",
            given_code="123"
        )
    except PasswordResetInvalid:
        print("The code you've provided is incorrect")
    except PasswordPolicyError:
        print("Password doesn't meet password policy!")
    else:
        print("Password has been reset!")

Getting user details
^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from aioaccount import UserIdError

    try:
        model = await user.get()
    except UserIdError:
        pass
    else:
        print(model.name)
