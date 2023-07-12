# hikari-atsume

[![ci](https://github.com/pmdevita/hikari-atsume/actions/workflows/ci.yml/badge.svg)](https://github.com/pmdevita/hikari-atsume/actions/workflows/ci.yml)
![mypy](https://badgen.net/badge/mypy/checked/2A6DB2)
![code-style-black](https://img.shields.io/badge/code%20style-black-black)

An opinionated Discord bot framework inspired by Django and built on 
top of Hikari, Tanjun, Ormar, and Alembic.

## Features

- Django-inspired design and philosophy
  - Automatic project scaffolding/file-based organization
  - Configuration instead of boilerplate
- Configure which components run in which servers
- Database ORM with Ormar
- Automatic database migrations with Alembic

## Alpha notes

This repo currently holds two projects, a rewrite of my Discord bot 
Beatrice, and hikari-atsume, 

Atsume is the next stage of my work on my bot. For a while, I've 
been thinking about how Django's solution of opinionated, helpful 
project scaffolding, seamless database integration, and flexible, 
powerful configuration would also make for a good development 
experience for Discord bots. Beatrice and [nextcord-ormar](https://github.com/pmdevita/nextcord-ormar) 
were both an attempt at implementing something like this, 
but Discord.py/Nextcord already provide a lot of framework-like 
features and this caused some friction in the implementation. 
Hikari and Tanjun are more barebones, and thus allow for more 
flexibility with stringing them together.

The whole thing is still getting figured out as I get a better 
understanding of Tanjun and Hikari and start porting code over from 
Beatrice and nextcord-ormar. Right now, you can see some things 
coming together in Atsume's modules. The main bot runner for Atsume 
is in `atsume.bot`, it's the largest mess in the bot, but 
it can bootstrap the bot, database, and components, so it's functionally
nearly complete. You can also look in the Beatrice package to get an
idea of how usage might work.

Once Atsume is in good shape, Beatrice will be moved out to it's own repo 
and Atsume will be put on PyPI.

Todo:
 - [x] Implement Django-like components and loading through configuration
 - [x] Implement per-guild and DM permissions
 - [x] Implement support for Ormar models
 - [ ] Implement Alembic migrations/port from nextcord-ormar
 - [x] Code clean up
 - [ ] Beatrice move out
 - [x] MyPy hints
 - [ ] Documentation
 - [ ] Test
 - [ ] Actions/Automation


## Special thanks to
- The Hikari Discord for help and feedback
- FasterSpeeding for Tanjun
- Lunarmagpie for help with the CI and linting
- The Django project for their amazing work and some 
code that I borrowed.


