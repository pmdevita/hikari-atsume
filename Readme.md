# hikari-atsume

[![ci](https://github.com/pmdevita/hikari-atsume/actions/workflows/ci.yml/badge.svg)](https://github.com/pmdevita/hikari-atsume/actions/workflows/ci.yml)
![mypy](https://badgen.net/badge/mypy/checked/2A6DB2)
![code-style-black](https://img.shields.io/badge/code%20style-black-black)


[Documentation](https://pmdevita.github.io/hikari-atsume/atsume.html)

An opinionated Discord bot framework inspired by Django and built on 
top of Hikari, Tanjun, Ormar, and Alembic.


## Features

- Django-inspired design and philosophy
  - Automatic project scaffolding/file-based organization
  - Configuration instead of boilerplate
- Configure which components run in which servers
- Database ORM with Ormar
- Automatic database migrations with Alembic

## Quick Start

### Installation

Create a new project directory and install hikari-atsume 
(make sure you are using Python 3.10+. If you are using Poetry, 
your Python dependency should be `python = "^3.10,<3.12"`)

```shell
# PyPI coming soon!

pip install git+https://github.com/pmdevita/hikari-atsume.git
```

### Start a new project

Now to start your new project, run 

```shell
atsume startproject my_bot
```

which should generate some files for your project. In `my_bot/local.py`, add your
Discord bot token in.


## Special thanks to
- The Hikari Discord for help and feedback
**- FasterSpeeding for Tanjun**
- Lunarmagpie for help with the CI and linting
- The Django project for their amazing work and some 
code that I borrowed.


