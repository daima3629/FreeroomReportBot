import discord
from discord.ext import commands
import json
import datetime
import traceback

ECOLOR = 0x34bf79
ERRCOLOR = 0xeb0000

class MainCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def check(self, ctx):
        try:
            cat = ctx.channel.category
            if not cat:
                embed = discord.Embed(
                    title = "エラー",
                    description = "チャンネルはカテゴリー内にありません。",
                    color = ERRCOLOR
                )
                return await ctx.send(embed=embed)
            with open("./data.json", "r") as f:
                data = json.load(f)
            ignores = data["ignores"].get(str(cat.id)) if data["ignores"].get(str(cat.id)) != None else []

            embed = discord.Embed(
                title = "checking...",
                description = "カテゴリー内の全チャンネルをチェックしています。\nしばらくお待ちください...",
                color = ECOLOR
            )
            await ctx.channel.send(embed=embed)

            count = 0
            found_chans = []
            for chan in cat.channels:
                try:
                    if chan.id in ignores:
                        continue
                    last = await chan.history(limit=1).flatten()
                    if not last:
                        continue
                    last_time = last[0].created_at
                    now = datetime.datetime.utcnow()
                    s = now - last_time
                    day = s.days
                    if day >= 30:
                        found_chans.append([f"#{chan.name}", day])
                        count += 1
                except discord.errors.Forbidden:
                    await ctx.send(f"> {chan.mention}の読み取り権限がありません！")
                    continue
            embed = discord.Embed(
                title = "Result",
                description = f"期限切れチャンネルが{count}個見つかりました。",
                color = ECOLOR
            )
            for info in found_chans:
                embed.add_field(
                    name = info[0],
                    value = f"経過日数: {info[1]}日"
                )
            return await ctx.send(embed=embed)
        except Exception as e:
            err = ''.join(traceback.TracebackException.from_exception(e).format())
            tz_jst = datetime.timezone(datetime.timedelta(hours=9))
            time = datetime.datetime.now(tz_jst).strftime("%Y/%m/%d %H:%M")
            embed = discord.Embed(
                title = "Unknown error happend",
                description = f"`MainCmds.check`\ntraceback:```{err}```"
            )
            embed.set_footer(text=time)
            err_chan = self.bot.get_channel(660855440665608212)
            return await err_chan.send(embed=embed)

    


def setup(bot):
    bot.add_cog(MainCmds(bot))
    print("maincmds loaded")