import lightbulb

plugin = lightbulb.Plugin("External")


@plugin.command
@lightbulb.option("query", "The thing to search.")
@lightbulb.command("google", "Let me Google that for you...")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_google(ctx: lightbulb.SlashContext) -> None:
    q = ctx.options.query

    if len(q) > 500:
        await ctx.respond("Your query should be no longer than 500 characters.")
        return

    await ctx.respond(f"<https://letmegooglethat.com/?q={q.replace(' ', '+')}>")


@plugin.command
@lightbulb.option("query", "The thing to search.")
@lightbulb.command("duckduckgo", "let me Duck Duck Go that for you...")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_duckduckgo(ctx: lightbulb.SlashContext) -> None:
    q = ctx.options.query

    if len(q) > 500:
        await ctx.respond("Your query should be no longer than 500 characters.")
        return

    await ctx.respond(f"<https://lmddgtfy.net/?q={q.replace(' ', '+')}>")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
