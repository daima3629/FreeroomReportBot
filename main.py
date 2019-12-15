import discord, datetime, json, math
from discord.ext import tasks
import traceback
client = discord.Client()

with open("config.json", "r") as f:
    config = json.load(f)
with open("data.json", "r") as f:
    data = json.load(f)

def jsonsave():
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

presence = "fr//help"
@client.event
async def on_ready():
    global presence
    pinchan = client.get_channel(652773329777721345)
    logchan = client.get_channel(652754897204412424)
    now = datetime.datetime.now()
    msg = await pinchan.send("> ping check")
    msg_time = msg.created_at
    ping = msg_time - now
    milisec = math.floor(ping.microseconds/1000)
    game = discord.Game("{} | Ping:{}ms".format(presence, str(milisec)))
    await client.change_presence(activity=game)
    print("Ready.")
    embed = discord.Embed(
        title = "Boot",
        description = "Boot Succesful",
        timestamp = datetime.datetime.now()
    )
    await logchan.send(embed=embed)

@tasks.loop(seconds=10)
async def ping():
    global presence
    if not client.is_ready():
        return
    pinchan = client.get_channel(652773329777721345)
    now = datetime.datetime.now()
    msg = await pinchan.send("> ping check")
    msg_time = msg.created_at
    ping = msg_time - now
    milisec = math.floor(ping.microseconds/1000)
    game = discord.Game("{} | Ping:{}ms".format(presence, str(milisec)))
    await client.change_presence(activity=game)
ping.start()

@tasks.loop(minutes=1)
async def checktasks():
    if not client.is_ready():
        return
    now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    if now_jst.hour == 0:
        if not now_jst.minute == 0:
            return
    else:
        return
    print("<<checktasks>>")
    for d in data["checktasks"]:
        cat = client.get_channel(d[0])
        s_chan = client.get_channel(d[1])
        ignores = data["ignores"].get(str(cat.id))
        count = 0
        embed = discord.Embed(
            title = "自動チェック",
            description = "午前0:00になりましたので、自動チェックを行います。\n除外登録されているチャンネルはないものとして扱われます。"
        )
        await s_chan.send(embed=embed)
        print("-----check <{}> -----".format(str(cat.id)))
        for chan in cat.channels:
            try:
                if ignores:
                    if chan.id in ignores:
                        print("Ignore <{}>".format(str(chan.id)))
                        continue
                last = await chan.history(limit=1).flatten()
                if not last:
                    print("Continue <{}>".format(str(chan.id)))
                    continue
                last_time = last[0].created_at
                now = datetime.datetime.now()
                s = now - last_time
                day = s.days
                if day > 30:
                    embed = discord.Embed(description="{}の有効期限が切れています。削除してください。".format(chan.mention))
                    await s_chan.send(embed=embed)
                    count += 1
                    print("Found <{}>".format(chan.id))
                    continue
                else:
                    print("Continue <{}>".format(str(chan.id)))
            except discord.errors.Forbidden:
                print("Forbidden <{}>".format(str(chan.id)))
                embed = discord.Embed(description="{}のメッセージ履歴を読む権限がないため、スキップされました。".format(chan.mention))
                await s_chan.send(embed=embed)
                continue
        await s_chan.send("> 期限切れチャンネルが {} 個見つかりました".format(str(count)))
        print("-----end check <{}> -----".format(str(cat.id)))
    print("<<checktasks>>")
checktasks.start()

async def help(message):
    embed = discord.Embed(
        title = "FreeroomReportBot",
        description = "ver 2.0 | Prefix `fr//`"
    )
    embed.add_field(
        name = "Explain", 
        value = "フリーカテゴリーのチャンネルの最終発言の日を確認し、\n発言から30日過ぎていれば通知してくれるBOTです。",
        inline = False
    )
    embed.add_field(
        name = "Commands",
        value = "--------",
        inline = False
    )
    embed.add_field(
        name = "`fr//help`",
        value = "このコマンドです。",
        inline = False
    )
    embed.add_field(
        name = "fr//check",
        value = """コマンドを打ったチャンネルのカテゴリー内の全チャンネルを確認します。
    ※チャンネルで一度も発言がない場合、期限は過ぎていないものとされます。""",
        inline = False
    )
    embed.add_field(
        name = "`fr//auto-on`",
        value = """毎日0:00(JST)に行われる自動スキャンに登録します。
    スキャンカテゴリーは発言チャンネルが入っているカテゴリー、
    通知チャンネルは発言チャンネルとなります。
    ※実行には`管理者`か`チャンネルの管理`権限が必要となります。""",
        inline = False
    )
    embed.add_field(
        name = "`fr//auto-off`",
        value = """自動スキャンへの登録を解除します。
    ※実行には`管理者`か`チャンネルの管理`権限が必要となります。""",
        inline = False
    )
    embed.add_field(
        name = "`fr//ignore [Channel_mention]`",
        value = """発言カテゴリーのスキャンから除外するチャンネルを指定できます。
    [Channel_mention]にチャンネルのメンションを指定してください。""",
        inline = False
    )
    embed.add_field(
        name = "`fr//obey [Channel_mention]`",
        value = """`fr//ignore`で除外したチャンネルを再度スキャンさせます。
    [Channel_mention]にチャンネルのメンションを指定してください。""",
        inline = False
    )
    embed.add_field(
        name="Other Information",
        value = "-----------------",
        inline = False
    )
    embed.add_field(
        name = "Developer",
        value = "*daima3629#1235*",
        inline = False
    )
    embed.add_field(name="招待リンク", value="[URL](https://discordapp.com/api/oauth2/authorize?client_id=650989851818328074&permissions=76816&scope=bot)", inline=False)
    embed.add_field(name="ソースコード", value="[URL](https://github.com/daima3629/FreeroomReportBot/)\n※このBOTはオープンソースですが、二次配布は禁止といたします。[ライセンス](https://github.com/daima3629/FreeroomReportBot/blob/master/LICENSE)", inline=False)
    _msg = """>>> **FreeroomReportBot v1.5**
Prefix : `fr//`

概要:
    フリーカテゴリーのチャンネルの最終発言の日を確認し、
    発言から30日過ぎていれば通知してくれるBOTです。
コマンド:
    `fr//help`
    　このコマンドです。
    `fr//check`
    　
    `fr//auto-on`
    　
    `fr//auto-off`
    　自動スキャンへの登録を解除します。
    　※実行には`管理者`か`チャンネルの管理`権限が必要となります。
その他情報:
    開発者:`daima3629#1235`
    招待リンク:
    　`https://discordapp.com/api/oauth2/authorize?client_id=650989851818328074&permissions=76816&scope=bot`
    このBOTのソースコード:
    　`https://github.com/daima3629/FreeroomReportBot/`
    """
    await message.channel.send(embed=embed)

async def check(message):
    category = message.channel.category
    if not category:
        embed = discord.Embed(title="エラー", description="発言チャンネルはカテゴリーの中に入っていません。")
        await message.channel.send(embed=embed)
        return
    ignores = data["ignores"].get(str(category.id))
    embed = discord.Embed(
        title = "チャンネルチェック",
        description = "発言カテゴリー内の全チャンネルの期限を確認します。\n除外登録されているチャンネルはないものとして扱われます。"
    )
    await message.channel.send(embed=embed)
    count = 0
    print("-----check <{}> -----".format(str(category.id)))
    for chan in category.channels:
        try:
            if ignores:
                if chan.id in ignores:
                    print("Ignore <{}>".format(str(chan.id)))
                    continue
            last = await chan.history(limit=1).flatten()
            if not last:
                print("Continue <{}>".format(str(chan.id)))
                continue
            last_time = last[0].created_at
            now = datetime.datetime.now()
            s = now - last_time
            day = s.days
            if day > 30:
                embed = discord.Embed(description="{}の有効期限が切れています。削除してください。".format(chan.mention))
                await message.channel.send(embed=embed)
                count += 1
                print("Found <{}>".format(chan.id))
            else:
                print("Continue <{}>".format(str(chan.id)))
        except discord.errors.Forbidden:
            print("Forbidden <{}>".format(str(chan.id)))
            embed = discord.Embed(description="{}のメッセージ履歴を読む権限がないため、スキップされました。".format(chan.mention))
            await message.channel.send(embed=embed)
            continue
    embed = discord.Embed(description="期限切れチャンネルが {} 個見つかりました".format(str(count)))
    await message.channel.send(embed=embed)
    print("-----end check <{}> -----".format(str(category.id)))

async def auto_on(message):
    per = message.author.guild_permissions
    if per.administrator or per.manage_channels:
        for d in data["checktasks"]:
            if d[0] == message.channel.category.id:
                embed = discord.Embed(
                title = "エラー",
                description = "このカテゴリーはすでに自動スキャンに登録されています。\n自動スキャンを解除したい場合は`fr//exclude`"
                )
                await message.channel.send(embed=embed)
                return

        embed = discord.Embed(
            title = "自動スキャン登録",
            description = "登録すると、毎日午前0:00に自動でカテゴリーをスキャンして報告してくれます。\n登録しますか？(y/n)"
        )
        await message.channel.send(embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel
        msg = await client.wait_for("message", check=check)
        if msg.content == "y":
            data["checktasks"].append([message.channel.category.id, message.channel.id])
            jsonsave()
            print("<Register>\n  category:{}\n  say_channel:{}".format(message.channel.category.id, message.channel.id))
            embed = discord.Embed(
                title = "登録完了",
                description = "正常に登録完了しました。これで次回午前0:00から自動スキャンを開始します。\n自動スキャンを解除したい場合は`fr//exclude`"
            )
            await message.channel.send(embed=embed)
        elif msg.content == "n":
            await msg.add_reaction("\U0001f44d")
            return
    else:
        embed = discord.Embed(
            title = "エラー",
            description = "このコマンドを実行するには\n・`管理者`\n・`チャンネルの管理`\nのどちらかの権限が必要です。"
        )
        await message.channel.send(embed=embed)
        return

async def auto_off(message):
    per = message.author.guild_permissions
    if per.administrator or per.manage_channels:
        exist = False
        for i,d in enumerate(data["checktasks"]):
            if d[0] == message.channel.category.id:
                num = i
                exist = True
                break
        if not exist:
            embed = discord.Embed(
                title = "エラー",
                description = "このカテゴリーは自動スキャンに登録されていません。"
            )
            await message.channel.send(embed=embed)
            return
        embed = discord.Embed(
            title = "自動スキャン解除",
            description = "解除すると、カテゴリーの自動スキャンはされなくなります。\n解除しますか？(y/n)"
        )
        await message.channel.send(embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel
        msg = await client.wait_for("message", check=check)
        if msg.content == "y":
            del data["checktasks"][num]
            jsonsave()
            print("<Exclude>\n  category:{}\n  say_channel:{}".format(message.channel.category.id, message.channel.id))
            embed = discord.Embed(
                title = "解除完了",
                description = "正常に解除完了しました。\n再度登録したい場合は`fr//regist`"
            )
            await message.channel.send(embed=embed)
        elif msg.content == "n":
            await msg.add_reaction("\U0001f44d")
            return
    else:
        embed = discord.Embed(
            title = "エラー",
            description = "このコマンドを実行するには\n・`管理者`\n・`チャンネルの管理`\nのどちらかの権限が必要です。"
        )
        await message.channel.send(embed=embed)
        return

async def ignore(message):
    per = message.author.guild_permissions
    if per.administrator or per.manage_channels:
        channel = message.channel_mentions
        category = message.channel.category
        if not channel:
            embed = discord.Embed(
                title = "エラー",
                description = "引数にチャンネルメンションを指定してください。"
            )
            await message.channel.send(embed=embed)
            return
        elif len(channel) > 1:
            embed = discord.Embed(
                title = "エラー",
                description = "引数が多すぎます。1つだけにしてください。"
            )
            await message.channel.send(embed=embed)
            return
        elif data["ignores"].get(str(category.id)):
            if channel[0].id in data["ignores"][str(category.id)]:
                embed = discord.Embed(
                    title = "エラー",
                    description = "そのチャンネルはすでに除外されています。"
                )
                await message.channel.send(embed=embed)
                return
        embed = discord.Embed(
            title = "除外チャンネル登録",
            description = "登録すると、発言カテゴリーをスキャンする際にこのチャンネルはないものとして扱われます。\n登録しますか？(y/n)"
        )
        await message.channel.send(embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel and (m.content == "y" or m.content == "n")
        msg = await client.wait_for("message", check=check)
        if msg.content == "n":
            await msg.add_reaction("\U0001f44d")
            return
        chan_id = channel[0].id
        if not str(category.id) in data["ignores"]:
            data["ignores"][str(category.id)] = []
            data["ignores"][str(category.id)].append(chan_id)
        else:
            data["ignores"][str(category.id)].append(chan_id)
        jsonsave()
        embed = discord.Embed(
            title = "除外チャンネル登録完了",
            description = "{0} を発言カテゴリーのスキャン対象から除外しました。\n再度スキャン対象にするには`fr//obey #{1}`".format(channel[0].mention, channel[0].name)
        )
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(
            title = "エラー",
            description = "このコマンドを実行するには\n・`管理者`\n・`チャンネルの管理`\nのどちらかの権限が必要です。"
        )
        await message.channel.send(embed=embed)
        return

async def obey(message):
    per = message.author.guild_permissions
    if per.administrator or per.manage_channels:
        channel = message.channel_mentions
        category = message.channel.category
        if not channel:
            embed = discord.Embed(
                title = "エラー",
                description = "引数にチャンネルメンションを指定してください。"
            )
            await message.channel.send(embed=embed)
            return
        elif len(channel) > 1:
            embed = discord.Embed(
                title = "エラー",
                description = "引数が多すぎます。1つだけにしてください。"
            )
            await message.channel.send(embed=embed)
            return
        elif not data["ignores"].get(str(category.id)):
            embed = discord.Embed(
                title = "エラー",
                descrption = "そのチャンネルは除外されていません。"
            )
            await message.channel.send(embed=embed)
            return
        elif not channel[0].id in data["ignores"][str(category.id)]:
            embed = discord.Embed(
                title = "エラー",
                descrption = "そのチャンネルは除外されていません。"
            )
            await message.channel.send(embed=embed)
            return
        embed = discord.Embed(
            title = "除外解除",
            description = "解除すると、次回スキャンからチャンネルはあるものとして扱われます。\n解除しますか？(y/n)"
        )
        await message.channel.send(embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel and (m.content == "y" or m.content == "n")
        msg = await client.wait_for("message", check=check)
        if msg.content == "n":
            await msg.add_reaction("\U0001f44d")
            return
        data["ignores"][str(category.id)].remove(channel[0].id)
        jsonsave()
        embed = discord.Embed(
            title = "除外解除完了",
            description = "{0}を除外チャンネルから解除しました。".format(channel[0].mention)
        )
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(
            title = "エラー",
            description = "このコマンドを実行するには\n・`管理者`\n・`チャンネルの管理`\nのどちらかの権限が必要です。"
        )
        await message.channel.send(embed=embed)
        return

#-------↓for BOT OP↓-------#
async def botop(message):
    global presence
    if not message.author.id == 570243143958528010:
        embed = discord.Embed(
            title = "エラー",
            description = "このコマンドはBOT開発者しか利用できません。"
        )
        await message.channel.send(embed=embed)
        return
    args = message.content.split()
    if len(args) == 1:
        embed = discord.Embed(title="BotOperationHelp")
        embed.add_field(name="`presence`", value="Change Bot presence.")
        embed.add_field(name="`stop`", value="Stop Bot.")
        #----------------------------------------------------#
        await message.channel.send(embed=embed)
    elif args[1] == "stop":
        embed=discord.Embed(description="BOTを終了しています...")
        await message.channel.send(embed=embed)
        exit()
    elif args[1] == "presence":
        presence = args[2]
        embed = discord.Embed(
            title = "Presence changed",
            description = "Presenceが`{}`に変更されました。\n次回pingチェック時に適用されます。".format(presence)
        )
        await message.channel.send(embed=embed)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    mentions = message.mentions
    if client.user in mentions:
        await message.channel.send("> Prefix -> `fr//help`")
        return
    if message.content.startswith("fr//"):
        if message.content == "fr//help":
            await help(message)

        elif message.content.startswith("fr//check"):
            await check(message)

        elif message.content == "fr//auto-on":
            await auto_on(message)
        elif message.content == "fr//auto-off":
            await auto_off(message)
        
        elif message.content.startswith("fr//ignore"):
            await ignore(message)
        elif message.content.startswith("fr//obey"):
            await obey(message)

        #-------↓for BOT OP↓-------#
        elif message.content.startswith("fr//botop"):
            await botop(message)

client.run(config["TOKEN"])