# hikari-atsume

[![ci](https://github.com/pmdevita/hikari-atsume/actions/workflows/ci.yml/badge.svg)](https://github.com/pmdevita/hikari-atsume/actions/workflows/ci.yml)
[![docs](https://github.com/pmdevita/hikari-atsume/actions/workflows/docs.yml/badge.svg)](https://pmdevita.github.io/hikari-atsume/)
![mypy](https://badgen.net/badge/mypy/checked/2A6DB2)
![code-style-black](https://img.shields.io/badge/code%20style-black-black)


[Documentation](https://pmdevita.github.io/hikari-atsume/)

An opinionated Discord bot framework inspired by Django and built on
top of [Hikari](https://github.com/hikari-py/hikari) and [PiccoloORM](https://github.com/piccolo-orm/piccolo/).

> Atsume is very much still in alpha and breaking changes should be expected. Progress may be slow as well.
If you have any feedback or advice, feel free to find me in the [Hikari Discord](https://discord.gg/Jx4cNGG).

> Following the refactor from Ormar to Piccolo and the dropping of Tanjun, the docs are
> completely out of date. Check out how the example bot works for now.

Atsume is a framework for Discord bots. It's designed for bots that go beyond simple responses or actions,
with integrated features to make state and lifecycle management easier.


## Features

- Automatic project scaffolding/file-based organization

Atsume splits a bot into multiple "apps". Each app is a self-contained
set of functionality, including commands and database tables.

- Configuration instead of boilerplate

Any server-side application is bound to need configuration. Atsume offers
a core settings package similar to Django, where you can configure settings in code or
read in values from environment variables.

Atsume extends this idea further into general configuration for how apps
interact with Discord. Apps can be enabled or disabled on a per-server basis. Developers
can also set up channel groups in their app, allowing users to configure which
channels the app runs in.

- Functionality split into modular, independent components

Much like Django, Atsume's core systems are designed as interfaces first.
Implementation can be configured and swapped.

- Automatically restart the bot on changes during development
- Database ORM and migrations with PiccoloORM


## Special thanks to
- davsda and the Hikari maintainers
- The Hikari Discord for help and feedback
- FasterSpeeding for [Tanjun](https://github.com/FasterSpeeding/Tanjun), Atsume's original command system
- Lunarmagpie for help with the CI and linting
- The [Django](https://www.djangoproject.com/) and [django-stubs](https://github.com/typeddjango/django-stubs) projects for their amazing work and some
code that I borrowed.
- My IRL friends who were my ~~guinea pigs~~ beta testers

"atsume" (集める) means "collecting", like how Atsume can collect multiple apps to run under one bot.
