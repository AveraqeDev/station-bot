import logging
import os
import traceback
from pathlib import Path

import hikari
import lightbulb
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from hikari.events.base_events import FailedEventT
from pytz import utc

import station_bot
from station_bot import Config, Database
from station_bot.utils import helpers

log = logging.getLogger(__name__)

bot = lightbulb.BotApp(
    token=Config.TOKEN,
    prefix=Config.PREFIX,
    owner_ids=Config.OWNER_IDS,
    case_insensitive_prefix_commands=True,
    help_slash_command=True,
    default_enabled_guilds=(Config.GUILD_ID,),
    intents=hikari.Intents.ALL,
)
bot.d._dynamic = Path("./data/dynamic")
bot.d._static = bot.d._dynamic.parent / "static"

bot.d.scheduler = AsyncIOScheduler()
bot.d.scheduler.configure(timezone=utc)

bot.load_extensions_from("./station_bot/extensions")


@bot.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.scheduler.start()
    bot.d.session = ClientSession(trust_env=True)
    log.info("AIOHTTP session started.")

    bot.d.db = Database(bot.d._dynamic, bot.d._static)
    await bot.d.db.connect()
    bot.d.scheduler.add_job(bot.d.db.commit, CronTrigger(second=0))


@bot.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent) -> None:
    await bot.rest.create_message(
        Config.LOG_CHANNEL_ID,
        (
            f"{station_bot.__productname__} is now online! "
            f"(Version {station_bot.__version__})"
        ),
    )


@bot.listen(hikari.StoppingEvent)
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.db.close()
    await bot.d.session.close()
    log.info("AIOHTTP session closed.")
    bot.d.scheduler.shutdown()

    await bot.rest.create_message(
        Config.LOG_CHANNEL_ID,
        (
            f"{station_bot.__productname__} is shutting down. "
            f"(Version {station_bot.__version__})"
        ),
    )


@bot.listen(hikari.DMMessageCreateEvent)
async def on_dm_message_create(event: hikari.DMMessageCreateEvent) -> None:
    if event.message.author.is_bot:
        return

    await event.message.respond("I cannot work in direct messages.")


@bot.listen(hikari.ExceptionEvent)
async def on_error(event: hikari.ExceptionEvent[FailedEventT]) -> None:
    raise event.exception


@bot.listen(lightbulb.CommandErrorEvent)
async def on_command_error(event: lightbulb.CommandErrorEvent) -> None:
    exc = getattr(event.exception, "__cause__", event.exception)

    if isinstance(exc, lightbulb.NotOwner):
        await event.context.respond("You need to be an owner to do that.")
        return

    # Add more errors when needed.

    try:
        err_id = helpers.generate_id()
        await bot.d.db.execute(
            "INSERT INTO errors(err_id, err_cmd, err_text) VALUES (?, ?, ?)",
            err_id,
            event.context.invoked_with,
            "".join(traceback.format_exception(event.exception)),
        )
        await event.context.respond(
            "Something went wrong. An error report has been created "
            f"(ID: {err_id[:7]})."
        )
        await bot.rest.create_message(
            Config.LOG_CHANNEL_ID, f"Error report created (ID: {err_id[:7]})."
        )
    finally:
        raise event.exception


def run() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot.run(
        activity=hikari.Activity(
            name=f"/help • Version {station_bot.__version__}",
            type=hikari.ActivityType.WATCHING,
        )
    )
