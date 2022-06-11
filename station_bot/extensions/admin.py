from __future__ import annotations

import logging
from io import BytesIO

import hikari
import lightbulb

import station_bot

log = logging.getLogger(__name__)

plugin = lightbulb.Plugin("Admin")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command(
    "shutdown", f"Shut {station_bot.__productname__} down.", ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_shutdown(ctx: lightbulb.SlashContext) -> None:
    log.info("Shutdown signal received.")
    await ctx.respond("Now shutting down.")
    await ctx.bot.close()


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("id", "The error reference ID.")
@lightbulb.command("error", "View an error.")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_error(ctx: lightbulb.SlashContext) -> None:
    if len(search_id := ctx.options.id) < 5:
        await ctx.respond("Your search should be at least 5 characters long.")
        return

    row = await ctx.bot.d.db.try_fetch_record(
        "SELECT * FROM errors "
        "WHERE err_id LIKE ? || '%'"
        "ORDER BY err_time DESC "
        "LIMIT 1",
        search_id,
    )

    if not row:
        await ctx.respond("No errors matching that reference were found.")
        return

    message = await ctx.respond("error found. Standby...")
    b = BytesIO(
        f"Command: /{row.err_cmd}\nAt: {row.err_time}\n\n{row.err_text}".encode()
    )
    b.seek(0)
    await message.edit(content=None, attachment=hikari.Bytes(b, f"err{row.err_id}.txt"))


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
