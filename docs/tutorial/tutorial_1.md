# Getting Started

Before learning how to use Atsume, it's recommended that you are familiar with the Python
language. You should also be familiar with SQL and one of the supported database
backends (SQLite, MySQL/MariaDB, or PostgreSQL). Knowledge of the Hikari, Tanjun, and
Ormar libraries is a plus, but this tutorial will try to cover the basics for these
libraries along the way.

## Registering a new bot with Discord.

This tutorial won't cover the details for registering a bot, but to summarize, you'll need to register a
bot on the [Discord Developer Portal](https://discord.com/developers/applications) (The Discord-IRC project has a good
tutorial [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)) and add it
to a Discord server to test and use it. You may also want to be familiar with what Intents are, especially if
you want to make a bot that responds to message commands.

## Installing Atsume

To get started, create a new project directory for your bot. It's recommended to install your
libraries into a virtual environment, or use Poetry to track your dependencies. SQLite is
generally recommended for use when developing, or as an easy way to get started for beginners.

```shell
# Install with your preferred database backend

pip install hikari-atsume[sqlite]

pip install hikari-atsume[mysql]

pip install hikari-atsume[postgresql]
```

## Creating the Atsume project

With our project folder created and Atsume installed, it's time to start the project.

Open a terminal in your project folder. If you are using a virtual enviroment or Poetry, activate the
environment for those. Then, run this command

```shell
atsume startproject my_bot

# If you get an error that there is no atsume command, try
python -m atsume startproject my_bot

```

where `my_bot` is the name of your bot project.

This will generate some files in your project folder, which should look like this.

```
my_bot
 |- local.py
 |- settings.py
manage.py

```

:::{admonition} What is scaffolding and why does Atsume use it?
:class: tip

In Atsume, your bot code is loaded automatically through configuration rather than requiring you
to implement the loading yourself. In order to do this, Atsume expects your project to contain certain Python
files with specific names, like the `local.py` and `settings.py` files for your bot module, and `apps.py`, `models.py`,
and `commands.py` for components as we'll see later.

Since setting up these files yourself can be a bit time-consuming, Atsume can automatically generate these files for
you and help "scaffold" your project. Once generated, all that should be left is to fill in the
blank with your new code.
:::
