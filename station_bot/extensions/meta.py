import datetime as dt
import logging
import platform
import time

import hikari
import lightbulb
from psutil import Process, virtual_memory

import station_bot
from station_bot import Config
from station_bot.utils import chron, helpers

log = logging.getLogger(__name__)

plugin = lightbulb.Plugin("Meta")


@plugin.command
@lightbulb.command("ping", "Get the average DWSP latency for the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_ping(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond(
        f"Pong! DWSP latency: {ctx.bot.heartbeat_latency * 1_000:,.0f} ms."
    )


@plugin.command
@lightbulb.command("about", f"View information about {station_bot.__productname__}.")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_about(ctx: lightbulb.SlashContext) -> None:
    if not (guild := ctx.get_guild()):
        return

    if not (me := guild.get_my_member()):
        return

    if not (member := ctx.member):
        return

    await ctx.respond(
        hikari.Embed(
            title=f"About {station_bot.__productname__}",
            description="Type `/stats` for bot runtime stats.",
            color=helpers.choose_color(),
            timestamp=dt.datetime.now().astimezone(),
        )
        .set_thumbnail(me.avatar_url)
        .set_author(name="Information")
        .set_footer(f"Requested by {member.display_name}", icon=member.avatar_url)
        .add_field("Authors", "\n".join(f"<@{i}>" for i in Config.OWNER_IDS))
        .add_field(
            "Contributors",
            f"View on [GitHub]({station_bot.__url__}/graphs/contributors)",
        )
        .add_field(
            "License",
            "[MIT License]" f"({station_bot.__url__}/blob/main/LICENSE)",
        )
    )


@plugin.command
@lightbulb.command("stats", f"View runtime stats for {station_bot.__productname__}.")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_stats(ctx: lightbulb.SlashContext) -> None:
    if not (guild := ctx.get_guild()):
        return

    if not (me := guild.get_my_member()):
        return

    if not (member := ctx.member):
        return

    with (proc := Process()).oneshot():
        uptime = time.time() - proc.create_time()
        uptime_str = chron.short_delta(dt.timedelta(seconds=uptime))
        cpu_time = chron.short_delta(
            dt.timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user),
            ms=True,
        )
        mem_total = virtual_memory().total / (1024**2)
        mem_of_total = proc.memory_percent()
        mem_usage = mem_total * (mem_of_total / 100)

    await ctx.respond(
        hikari.Embed(
            title=f"Runtime statistics for {station_bot.__productname__}",
            description="Type `/about` for general bot information.",
            color=helpers.choose_color(),
            timestamp=dt.datetime.now().astimezone(),
        )
        .set_thumbnail(me.avatar_url)
        .set_author(name="Information")
        .set_footer(f"Requested by {member.display_name}", icon=member.avatar_url)
        .add_field("Bot version", station_bot.__version__, inline=True)
        .add_field("Python version", platform.python_version(), inline=True)
        .add_field("Hikari version", hikari.__version__, inline=True)
        .add_field("Uptime", uptime_str, inline=True)
        .add_field("CPU time", cpu_time, inline=True)
        .add_field(
            "Memory usage",
            f"{mem_usage:,.3f}/{mem_total:,.0f} MiB ({mem_of_total:,.0f}%)",
            inline=True,
        )
        .add_field(
            "Database calls",
            f"{(c := ctx.bot.d.db.calls):,} ({c/uptime:,.3f} per second)",
        )
    )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
