## Message Components

Buttons on messages stuff. We model after React/component-based UI libraries,
leading with a declarative strategy.

Two types - Message Component and Modal Component

### Message Component

These can be attached to an existing message or replied with.

```python
ctx.respond(NameComponent)

NameComponent.attach_message(message)

```

They are defined as dataclasses. Variables defined on the
class are *state*. They should be a JSON-ifiable type, or
one of a few Hikari types (Member, User, Channel, Role, etc.)


```python
class NameComponent(Component):
    name: Optional[str] = None

    def __init__(self, name: str):
        self.name = name

    def change_name(self, event: ButtonEvent):
        self.name = event.author.display_name

    def render(self):
        return Message(
            f"Your name is {self.name}!",
            component=Button(self.change_name, "Change to me")
        )
```

"But pmdevita!" I hear you say "Aren't class components bad for
reusability?" Well yeah maybe a little bit, but we have
class composability in Python, that's kind of what I'm banking on.

```python

# ComponentState is a Descriptor
class NameState(ComponentState[str]):
    # Tie this to the generic type
    state: str = ""

    def change_name(self, event: ButtonEvent):
        self.state = event.author.display_name



class NameComponent(NameState["name"], Component):
    name = NameState()

    def render(self):
        return Message(
            f"Your name is {self.name}!",
            component=Button(self.name.change_name, "Change to me")
        )



```

This isn't going to be as air-tight as React, but we also don't
have to deal with props.


### Modal Component

Real quick because they're easy, this is mostly configuration
since these can only contain text boxes. It's a dataclass.

```python

class ContactModal(Modal):
    first_name = TextInput(label="First Name")
    bio = ParagraphInput(label="Bio")

```

Maybe an alternative, programmatic way to make them?

```python
modal = ContactModal(
    TextInput(label="First Name"),
    ParagraphInput(label="Bio")
)
```


# Channel Handles

Applications for a Discord bot often need to be configured to use or listen to
specific channels. This tends to be something that you must reimplement per
app, which usually then involves

- A command for configuring the channel
- A database table for keeping track of the channel
- Filtering of incoming events to only those allowed by the configuration
- Lookups when needing to interact with that channel

Channel handles seeks to abstract this all away by allowing apps to
configure a set of channel names as part of their AppConfig. Atsume then takes care
of configuring these channels and keeping track of them. Apps can use handles in
things like event decorators or to lookup a channel for a smoother
programming experience.


## Use Cases

Channel handles need to be able to solve all common use cases, if not all possible
use cases. In order to do that, we need to examine how applications use channels.

### Splatgear

Splatgear is an application for receiving alerts when gear with specific
attributes is on sale in-app for Splatoon 2/3.


#### Configuring user alerts

Users interact with the bot through commands. This could be done in almost any channel
but server admins may want to restrict it to a bot channel or something.

#### Sending user alerts

Users have individual desires for gear so the most sensible thing to do is to DM
them when the gear they want is available.

#### Conclusion

Splatgear needs a general channel to set up configuration with users (or DMs) and
DMs to send alerts. The usecase is fairly standard and doesn't have much need
for handles.

### DND Messaging

DND Messaging is an April Fool's day joke application. Users are randomly given
stats and when they send a message, do a skill check against their stats. If they
fail, AI rewrites their message.

#### Stats Channel

DND Messaging publishes server user stats into a channel that everyone can look at.
This should be a single configured channel.

#### "Game Active" Channels

DND Messaging as it exists currently takes place in any channel of a server
with a stats channel. That being said, it may be useful to allow server owners to
configure which channels have the game running active in case they need a safe zone.

#### Conclusion

There may be a distinction made between channels for listening or channels for
messaging. For the "Game Active" channels, many channels can be assigned or allowed,
but for the stats channel, it *must* be a single channel. Channel handles might
be useful for both paradigms at once though, so maybe a channel handle can be
configured to be of a single or multiple type?

### Hurricane Warning

This app was never completed but presented a unique use for channels that
may be worth considering with handles. When a new hurricane is detected and
predicted to aim near any server members, a new channel in the server is created
and the given users are invited in. The bot then periodically messages the channel
with weather updates. The channel can then be deleted or archived by the server
owner to ignore it or to clean up afterwards.

#### Hurricane Config

Users can talk to the bot to configure their location for hurricane updates. The
bot sends them to a website with their Discord ID where they register their location.
Works the same as other configuration command channel needs.

#### Hurricane Watch channel

A channel created by the bot for a hurricane for it to send updates and
encourage topical discussion between members.

#### Conclusion

This is a very dicey use case and it's so removed from other examples, I'm not
sure if it's possible to service under the same paradigm. Whereas other uses have
a fixed number of channels, tied to existing or user controlled channels,
allowing apps to dynamically register channels just might not make sense for this.

For one thing, it seems wrong that an app could have an infinite number of handles,
as this would entail. The particularities of enumerating them makes this seem like
the wrong place to through them in.

I'm also not sure if this shouldn't be implemented for the usecase. We need to map
hurricanes to guilds and channels. Handles will probably often think in context of
a guild, not a super context of all guilds.

Ultimately I think hurricane channels likely need to be implemented from scratch
for the application, and I think knowing this lays out a key boundary for the
handles system.


#### Postscript: How would hurricane actually configure then?

App would keep a table of hurricanes and a table of guild-user locations. When
hurricane and users match, it creates another channel and keeps track in another table
of hurricane-guild channels. It would then lookup channels for messaging updates by
hurricane-guild.

It's really hard to say how we could abstract this any further. We will always need to
know hurricane and guild at runtime anyways, we can't handwave away this lookup any further.

### Star Board

Star Board is an application that allows users to save the "best of" messages in
a server. Users react with a star emote to a message, and that message is reposted
in a "star board" channel if enough users react to it.

#### Star Board Channel

Where the starred messages get posted. Should be a single channel.

#### Star board operating channels

Where messages that are starred can be sent to. Could actually be pretty useful
in case there are some private channels you'd rather not leak messages from.

#### Conclusion

Very standard, similar to other applications.



## Organized thoughts from use cases

Based on observations from use cases, here is what I think would be most useful.

- Channels can be configured to require a single target or allow multiple targets.
- Multiple target channels can have defaults for all channels in a server
(allow or deny all) and then can have individual channel overrides.
- Apps can require a channel be configured in order to enable use in a server.
- Servers can configure a default "bot" channel for bot activity. Apps with single
targets can opt to default to the bot channel if no specific channel is configured.
- Single target channels can be looked up by handle name, multiple target channels
cannot, they can only be used in command/event receivers. If possible, we should use
types to ensure users don't accidentally try to lookup multiple target channels
(if it's only detected at runtime it's probably going to be too late).
  - As an addendum, it may be possible to do multiple target lookups but IDK if
  it should be encouraged.
- As handles do not help every use case, handles are generally optional. Apps
should never be required to use them to interact with channels.

Single target should be called "interaction channel" and multi target should be "listening channels".
