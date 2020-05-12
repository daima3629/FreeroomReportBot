import discord
from discord.ext import commands
from discord.ext import tasks
import json
import datetime
import traceback

with open("config.json", "r") as f:
    config = json.load(f)

INITIAL_EXTENSIONS = [
    "cogs.maincmds",
    "cogs.infocmds"
]


class FreeRoomReportBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="fr//", help_command=None)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except:
                traceback.print_exc()
        
        self.ECOLOR = 0x34bf79
        self.ERRCOLOR = 0xeb0000

    async def on_ready(self):
        with open("data.json", "r") as f:
            data = json.load(f)
            repair = data["bot"]["repair"]
        if repair:
            await self.change_presence(activity=discord.Game("fr//help | Repairing"), status=discord.Status.do_not_disturb)
        else:
            await self.change_presence(activity=discord.Game("fr//help | Online"), status=discord.Status.online)
        self.error_channel = self.get_channel(660855440665608212)
        print("---------------------")
        print(f"FreeRoomReportBot Online\nID: {self.user.id}")
        return

    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.MissingPermissions):
            embed = discord.Embed(
                title="Error",
                description="コマンド実行に必要な権限がありません。\nhelpを確認してください。",
                color=self.ERRCOLOR
            )
            return await ctx.send(embed=embed)

        err_str = ''.join(traceback.TracebackException.from_exception(e).format())
        tz_jst = datetime.timezone(datetime.timedelta(hours=9))
        time = datetime.datetime.now(tz_jst).strftime("%Y/%m/%d %H:%M")
        command_name = ctx.command.name
        cog_name = ctx.command.cog.__class__.__name__
        embed = discord.Embed(
            title="Unknown Error happend",
            description=f"{command_name}.{cog_name}\ntraceback:```py{err_str}```",
            color=self.ERRCOLOR
        )
        embed.set_footer(text=time)
        await self.error_channel.send(embed=embed)


if __name__ == "__main__":
    bot = FreeRoomReportBot()
    bot.run(config["DISCORD_TOKEN"])
