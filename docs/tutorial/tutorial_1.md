# Getting Started

Before learning how to use Atsume, it's recommended that you are familiar with the Python 
language. You should also be familiar with SQL and one of the supported database 
backends (SQLite, MySQL/MariaDB, or PostgreSQL). Knowledge of the Hikari, Tanjun, and 
Ormar libraries is a plus, but this tutorial will try to cover the basics for these 
libraries along the way.

## Installing Atsume

To get started, create a new project directory for your bot. It's recommended to install your 
libraries into a virtual environment, or use Poetry to track your dependencies.

:::{tip}
At the moment, Atsume is not yet available on PyPI, but it will be soon once 
the proper release processes have been ironed out. This also means database 
libraries need to be installed directly, rather than as extras from Atsume.
:::

```shell
# pip
pip install https://github.com/pmdevita/hikari-atsume.git

# poetry
poetry install https://github.com/pmdevita/hikari-atsume.git
```

You'll also need to install database libraries for your preferred database 
backend. If you are unsure of which database backend to use, it's recommended 
to start with SQLite.

```shell
# Install the corresponding libraries for your backend
pip install aiosqlite
pip install aiomysql PyMySQL
pip install aiopg psycopg2-binary

poetry add aiosqlite
poetry add aiomysql PyMySQL
poetry add aiopg psycopg2-binary

```

## Creating the Atsume project

With our project folder created and Atsume installed, it's time to start the project.

Open a terminal in your project folder. If you are using a virtual enviroment or Poetry, activate the 
environment for those. Then, run this command 

```shell
atsume startproject my_bot
```

where `my_bot` is the name of your bot project.

This should generate some files in your project folder, which should not look like this.

```
my_bot
 |- local.py
 |- settings.py
manage.py

```

:::{admonition} What is scaffolding?
:class: tip

To help ease the creation of new projects and components, Atsume provides tools to "scaffold" or generate 
new Python files. You could set up the files yourself, but it's easier to let the command line tools help you.
:::









