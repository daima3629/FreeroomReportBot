import discord
from discord.ext import commands
import json
import datetime
import traceback

ECOLOR = 0x34bf79
ERRCOLOR = 0xeb0000
reactions = [
    "👍",
    "👎"
]


class MainCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check(self, ctx):
        try:
            cat = ctx.channel.category
            if not cat:
                embed = discord.Embed(
                    title="エラー",
                    description="チャンネルはカテゴリー内にありません。",
                    color=ERRCOLOR
                )
                return await ctx.send(embed=embed)
            with open("./data.json", "r") as f:
                data = json.load(f)
            ignores = data["ignores"].get(str(cat.id)) if data["ignores"].get(str(cat.id)) is not None else []

            embed = discord.Embed(
                title="checking...",
                description="カテゴリー内の全チャンネルをチェックしています。\nしばらくお待ちください...",
                color=ECOLOR
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
                title="Result",
                description=f"期限切れチャンネルが{count}個見つかりました。",
                color=ECOLOR
            )
            for info in found_chans:
                embed.add_field(
                    name=info[0],
                    value=f"経過日数: {info[1]}日"
                )
            return await ctx.send(embed=embed)
        except Exception as e:
            err = ''.join(traceback.TracebackException.from_exception(e).format())
            tz_jst = datetime.timezone(datetime.timedelta(hours=9))
            time = datetime.datetime.now(tz_jst).strftime("%Y/%m/%d %H:%M")
            embed = discord.Embed(
                title="Unknown error happened",
                description=f"`MainCmds.check`\ntraceback:```{err}```"
            )
            embed.set_footer(text=time)
            err_chan = self.bot.get_channel(660855440665608212)
            return await err_chan.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channel=True)
    async def settings(self, ctx, command, *args):
        if command == "ignore":
            if not ctx.message.category:
                embed = discord.Embed(
                    title="Error",
                    description="コマンド実行チャンネルはカテゴリー内に入っていません。",
                    color=ERRCOLOR
                )
                return await ctx.send(embed=embed)

            if not ctx.message.channel_mentions:
                embed = discord.Embed(
                    title="Error",
                    description="チャンネルメンションを指定してください。",
                    color=ERRCOLOR
                )
                return await ctx.send(embed=embed)
            channel = ctx.message.channel_mentions[0]
            category_id = ctx.message.category.id
            with open("./data.json", "r") as f:
                data = json.load(f)
            if channel.id in data["ignores"][category_id]:
                embed = discord.Embed(
                    title="Error",
                    description="指定されたチャンネルはすでに除外されています。",
                    color=ERRCOLOR
                )
                return await ctx.send(embed=embed)

            embed = discord.Embed(
                title="Confirm",
                description=f"{channel.mention}をこのカテゴリーのチャンネルチェックから除外しますか？",
                color=ECOLOR
            )
            msg = await ctx.send(embed=embed)
            await msg.add_reaction(reactions[0])
            await msg.add_reaction(reactions[1])
            reac, _ = await self.bot.wait_for(
                "reaction_add",
                check=lambda reac, user: ctx.author == user and str(reac) in reactions
            )
            if str(reac.emoji) == reactions[0]:
                if not data["ignores"].get[category_id]:
                    data["ignores"][category_id] = []
                data["ignores"][category_id].append(channel.id)
                with open("./data.json", "w") as f:
                    json.dump(data, f)
                embed = discord.Embed(
                    title="Ignore Success",
                    description=f"{channel.mention}をチェックから除外しました。",
                    color=ECOLOR
                )
                return await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="中断",
                    description=":-1:リアクションが押されたので処理を中断しました。",
                    color=ECOLOR
                )
                return await ctx.send(embed=embed)

        elif command == "obey":
            if not ctx.message.category:
                embed = discord.Embed(
                    title="Error",
                    description="コマンド実行チャンネルはカテゴリー内に入っていません。",
                    color=ERRCOLOR
                )
                return await ctx.send(embed=embed)

            if not ctx.message.channel_mentions:
                embed = discord.Embed(
                    title="Error",
                    description="チャンネルメンションを指定してください。",
                    color=ERRCOLOR
                )
                return await ctx.send(embed=embed)

            channel = ctx.message.channel_mentions[0]
            category_id = ctx.message.category.id
            with open("./data.json", "r") as f:
                data = json.load(f)
            if channel.id not in data["ignores"][category_id]:
                embed = discord.Embed(
                    title="Error",
                    description="指定されたチャンネルは除外されていません。",
                    color=ERRCOLOR
                )
                return await ctx.send(embed=embed)

            embed = discord.Embed(
                title="Confirm",
                description=f"{channel.mention}をこのカテゴリーのチャンネルチェック対象に戻しますか？",
                color=ECOLOR
            )
            msg = await ctx.send(embed=embed)
            await msg.add_reaction(reactions[0])
            await msg.add_reaction(reactions[1])
            reac, _ = await self.bot.wait_for(
                "reaction_add",
                check=lambda reac, user: ctx.author == user and str(reac) in reactions
            )
            if str(reac.emoji) == reactions[0]:
                data["ignores"][category_id].remove(channel.id)
                with open("./data.json", "w") as f:
                    json.dump(data, f)
                embed = discord.Embed(
                    title="Ignore Success",
                    description=f"{channel.mention}をチェック対象に戻しました。",
                    color=ECOLOR
                )
                return await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="中断",
                    description=":-1:リアクションが押されたので処理を中断しました。",
                    color=ECOLOR
                )
                return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MainCmds(bot))
    print("maincmds loaded")
