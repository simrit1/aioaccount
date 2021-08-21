# aioaccount
Utility for user account creation, modification & email confirmation.

## Installation
`pip3 install aioaccount`

## Features
- Security.
- Easy to use.
- Removes common boilerplate code.
- SMTP support.
- Email template support with jinja2.
- Mongodb, postgresql, mysql & sqlite support.
- Full unit tests.
- Full documentation.
- Uses aiojobs to spawn SMTP background jobs.

## Security
- All passwords are hashed using bcrypt.
- Password policies.
- Password reset code expiration.
- Email validation.
