import discord
from discord.ext import commands
from discord.ext import tasks
import json
import datetime
import traceback

with open("config.json", "r") as f:
    config = json.load(f)

INITIAL_EXTENSIONS = [
    "cogs.maincmds"
]

ERR_COLOR = 0xeb0000

class FreeRoomReportBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="fr//", help_command=None)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except:
                traceback.print_exc()

    async def on_ready(self):
        with open("data.json", "r") as f:
            data = json.load(f)
            repair = data["bot"]["repair"]
        if repair:
            await self.change_presence(activity=discord.Game("fr//help | Repairing"), status=discord.Status.do_not_disturb)
        else:
            await self.change_presence(activity=discord.Game("fr//help | Online"), status=discord.Status.online)
        print("---------------------")
        print(f"FreeRoomReportBot Online\nID: {self.user.id}")
        return

    async def on_command_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.MissingPermissions):
            embed = discord.Embed(
                title="Error",
                description="コマンド実行に必要な権限がありません。\nhelpを確認してください。"
            )


if __name__ == "__main__":
    bot = FreeRoomReportBot()
    bot.run(config["DISCORD_TOKEN"])
