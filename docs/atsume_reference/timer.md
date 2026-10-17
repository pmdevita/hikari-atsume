# Timer

Tanjun's built-in scheduling is useful for running functions on a regular interval. However, for functions that
need to run at variable times with extra context, this may not be enough. To handle tasks like this, you
can use atsume's Timer.

## Setup

Add Timer to your extensions.

```python
# bot/settings.py

EXTENSIONS = [
    "atsume.extensions.timer.hook_extension"
]

```

## Usage

You can request the Timer through Alluka in a command. From there, you can pass it an async function and a datetime
to run it at.

```python
import hikari
import alluka
import atsume
from atsume.extensions.timer import Timer
from datetime import datetime, timedelta


@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("schedule")
async def schedule(ctx: atsume.Context, timer: alluka.Injected[Timer]) -> None:
    timer.schedule_task(datetime.now() + timedelta(seconds=30), callback, [ctx, ctx.member])


async def callback(ctx: atsume.Context, member_name: hikari.Member) -> None:
    await ctx.respond(f"Delayed hello to {member_name.display_name}")


```
