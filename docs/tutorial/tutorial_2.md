# Configuring Atsume

Now that we have our new Atsume project, let's take a look at the `local.py` and `settings.py` files 
in your new `my_bot` directory.

## The Settings Files

Atsume uses two settings files, `local.py` and `settings.py`. In Atsume, settings are set by declaring 
variables inside these files. Settings can be declared in either file, but anything set in 
`local.py` overrides settings in `settings.py`. You should set any kind of "environment-specific" or
secret settings, like whether to run in debug mode or your Discord bot token, in your `local.py` 
file. Your `settings.py` is for any settings that should always stay the same, or to make defaults 
for any settings you'd set in your `local.py` file.

:::{hint}
If you are using git, add 
the `local.py` file to your `.gitignore` file 
so you don't accidentally make your bot token public!
:::

## Configuring the bot

Let's set the Discord bot token for our new Atsume project. In your `local.py` file, set the 
`TOKEN` variable to your Discord bot token. If you haven't made one yet, you can log into 
the [Discord Developer Portal](https://discord.com/developers/applications) and make one.

Once you have your token, set the `TOKEN` string to it.

```python
# my_bot/local.py

TOKEN = "TEyNzAzMY5MjYzxODE1MMTA5..."

```

Since we'll want to add message commands later (commands that you trigger by sending a message in a Discord channel), 
we'll need to make sure we have the message content intent. If you haven't enabled it on your bot, you'll want to 
do that in the [Discord Developer Portal](https://discord.com/developers/applications) 
(small tutorial [here](https://umod.org/community/discord/40519-how-to-enable-message-content-intent)).

```python
# my_bot/settings.py
import hikari

INTENTS = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT
```

## Running the bot

Now that we have our bot token configured, we can run our new Discord bot. To do so, 
run `python manage.py run`. If all goes well, you should see in the console something like.

```
hikari.bot: started successfully in approx 1.20 seconds
```


With this, we should be ready to create our first component!
