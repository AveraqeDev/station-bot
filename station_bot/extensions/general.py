import logging
import typing as t

import hikari
import lightbulb

from station_bot import Config

log = logging.getLogger(__name__)

plugin = lightbulb.Plugin("General")

NOTIFICATION_MAP: t.Mapping[str, int] = {
    "streams": Config.STREAMS_ROLE_ID,
}


async def update_member_count() -> None:
    channel = await plugin.bot.rest.fetch_channel(Config.MEMBER_COUNT_CHANNEL_ID)

    if not isinstance(channel, hikari.GuildVoiceChannel):
        return

    member_count = len(
        [
            m
            async for m in plugin.bot.rest.fetch_members(Config.GUILD_ID)
            if not m.is_bot
        ]
    )

    await channel.edit(name=f"Members: {member_count}")


@plugin.listener(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    await update_member_count()


@plugin.listener(hikari.MemberCreateEvent)
async def on_member_join(event: hikari.MemberCreateEvent) -> None:
    if event.member.guild_id != Config.GUILD_ID:
        return

    log.info(f"Member '{event.member.display_name}' joined")
    await update_member_count()


@plugin.listener(hikari.MemberDeleteEvent)
async def on_member_leave(event: hikari.MemberDeleteEvent) -> None:
    member = event.old_member

    if not member:
        return

    if member.guild_id != Config.GUILD_ID:
        return

    log.info(f"Member '{member.display_name}' left")
    await plugin.bot.rest.create_message(
        Config.LOG_CHANNEL_ID,
        f"{member.display_name} is no longer in the server. (ID: {member.id})",
    )
    await update_member_count()


@plugin.listener(hikari.GuildReactionAddEvent)
async def on_reaction_add(event: hikari.GuildReactionAddEvent) -> None:
    if event.message_id != Config.RULES_MESSAGE_ID:
        return

    if Config.PASSENGER_ROLE_ID in event.member.role_ids:
        return

    await event.member.add_role(Config.PASSENGER_ROLE_ID)


@plugin.listener(hikari.GuildReactionDeleteEvent)
async def on_reaction_delete(event: hikari.GuildReactionDeleteEvent) -> None:
    if event.message_id != Config.RULES_MESSAGE_ID:
        return

    member = await plugin.bot.rest.fetch_member(Config.GUILD_ID, event.user_id)

    if not Config.PASSENGER_ROLE_ID in member.role_ids:
        return

    await member.remove_role(Config.PASSENGER_ROLE_ID)


@plugin.command
@lightbulb.option("type", "Type of notification to receive.")
@lightbulb.command("notify", "Toggle subscription of a type of notification.")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_notify(ctx: lightbulb.SlashContext) -> None:
    if not ctx.channel_id == Config.ROLE_ASSIGN_CHANNEL_ID:
        await ctx.respond(
            f"This command can only be used in <#{Config.ROLE_ASSIGN_CHANNEL_ID}>.",
            delete_after=5,
        )
        return

    if not ctx.member:
        return

    type = ctx.options.type.lower()

    if not (role := NOTIFICATION_MAP.get(type)):
        await ctx.respond(
            "That is not a valid notification type.\nValid types are: "
            + ", ".join(NOTIFICATION_MAP.keys()),
            delete_after=5,
        )
        return

    if role in ctx.member.role_ids:
        await ctx.member.remove_role(role)
        await ctx.respond(
            f"You will no longer receive {type} notifications.", delete_after=5
        )
    else:
        await ctx.member.add_role(role)
        await ctx.respond(f"You will now receive {type} notifications.", delete_after=5)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
