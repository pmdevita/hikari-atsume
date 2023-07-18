# Ideas for improving the Tanjun docs

## Annotated commands can be hooked on to a bot

Docs currently show the following without describing how to use it in a Component

```python
@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("hi", "hello", "hey", "howdy")
@tanjun.as_slash_command("hi", "Bot says hi")
async def hello(ctx: tanjun.abc.Context, member: Annotated[Optional[Member], "The user to say hi to.", Positional()] = None):
    member = member if member else ctx.member
    await ctx.respond(f"Hi {member.display_name}!")
```

Component version (unless you want to use load_scope)

```python
@component.with_command(follow_wrapped=True)
@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("hi", "hello", "hey", "howdy")
@tanjun.as_slash_command("hi", "Bot says hi")
async def hello(ctx: tanjun.abc.Context, member: Annotated[Optional[Member], "The user to say hi to.", Positional()] = None):
    member = member if member else ctx.member
    await ctx.respond(f"Hi {member.display_name}!")
```


## Annotated commands: Optional arguments are not positional by default

This is the default in Discord.py. Expected `-prefix hi @user` to output `Hi user!` but it would 
not receive the argument. For this example, the correct command is `-prefix hi --member user`.

```python
@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("hi", "hello", "hey", "howdy")
@tanjun.as_slash_command("hi", "Bot says hi")
async def hello(ctx: tanjun.abc.Context, member: Annotated[Optional[Member], "The user to say hi to."] = None):
    member = member if member else ctx.member
    await ctx.respond(f"Hi {member.display_name}!")
```

You can make the command positional by adding `Positional()` (note the instantiation) to the Annotated type fields.

```python
@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("hi", "hello", "hey", "howdy")
@tanjun.as_slash_command("hi", "Bot says hi")
async def hello(ctx: tanjun.abc.Context, member: Annotated[Optional[Member], "The user to say hi to.", Positional()] = None):
    member = member if member else ctx.member
    await ctx.respond(f"Hi {member.display_name}!")
```


# Questions

1. How do I store data in a component between commands? (Discord.py just used a class for their extensions, not
sure where to store data here.)
   - You can just store it in the script scope, seems to be OK and is kinda done in the official bot
2. Can I access the bot object from the Component?
   - Yes, it's the `tanjun.Client` object
3. Can I respond to malformed message commands with custom help responses?
4. Can I hook into commands/event listeners and deny them before they are run? (Doing some per-guild permissions stuff)
    - Yes you can do `add_check` on a Component to add a permissions check. However,
   this won't help for event listeners.
      - Did it myself since Atsume currently has to wrap event listeners anyways 😎
      - Also did it for Component open, close, and scheduler


# Ormar 

- Autoincrement is on by default on a primary key integer and this blocks manually setting 
it in some cases (for example, creating an id of 0)
