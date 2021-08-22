.. aioaccount documentation master file, created by
   sphinx-quickstart on Sat Aug 21 14:39:59 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aioaccount's documentation!
======================================
Utility for user account creation, modification & email confirmation.

Installation
------------
`pip3 install aioaccount`

Features
--------
- Security.
- Easy to use.
- Removes common boilerplate code.
- SMTP support.
- Email template support with jinja2.
- Mongodb, postgresql, mysql & sqlite support.
- Full unit tests.
- Full documentation.
- Uses aiojobs to spawn SMTP background jobs.

Security
--------
- All passwords are hashed using bcrypt.
- Password policies.
- Password reset code expiration.
- Email validation.

Documentation Contents
-----------------------
.. toctree::
   :maxdepth: 4

   intro
   examples
   account_handler
   user
   models
   errors
   engines
   password_policy
   smtp
   low_level_db


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
