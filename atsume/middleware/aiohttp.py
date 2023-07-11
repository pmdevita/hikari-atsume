import aiohttp
import alluka
import tanjun


def hook_aiohttp(c: alluka.Injected[tanjun.abc.Client]) -> None:
    @c.with_client_callback(tanjun.ClientCallbackNames.STARTING)
    async def on_starting(client: alluka.Injected[tanjun.abc.Client]) -> None:
        client.set_type_dependency(aiohttp.ClientSession, aiohttp.ClientSession())

    @c.with_client_callback(tanjun.ClientCallbackNames.CLOSED)
    async def on_closed(session: alluka.Injected[aiohttp.ClientSession]) -> None:
        await session.close()
