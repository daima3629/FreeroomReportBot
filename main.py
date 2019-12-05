import discord, datetime, json
client = discord.Client()

with open("config.json", "r") as f:
    config = json.load(f)

@client.event
async def on_ready():
    game = discord.Game("type fr//help")
    await client.change_presence(activity=game)
    print("Ready.")

async def help(message):
    msg = """>>> **FreeroomReportBot v1.0**
Prefix : `fr//`

概要:
    フリーカテゴリーのチャンネルの最終発言の日を確認し、
    発言から30日過ぎていれば通知してくれるBOTです。
コマンド:
    `fr//help`
    　このコマンドです。
    `fr//check [Category_ID]`
    　[Category_ID]を指定すればそのIDのカテゴリー内の全チャンネルの最終発言日を確認し、
    　最終発言から30日過ぎていた場合通知してくれます。
    　[Category_ID]を指定しなかった場合、コマンドを打ったチャンネルのカテゴリー内の全チャンネルを
    　確認します。
    　※チャンネルで一度も発言がない場合、期限は過ぎていないものとされます。
その他情報:
    開発者:`daima3629#1235`
    招待リンク:
    　`https://discordapp.com/api/oauth2/authorize?client_id=650989851818328074&permissions=76816&scope=bot`
    このBOTのソースコード:
    　`https://github.com/daima3629/FreeroomReportBot/`
    """
    await message.channel.send(msg)

async def check(message):
    sliced = message.content.split()
    if len(sliced) == 2:
        category = client.get_channel(int(sliced[1]))
        if not category:
            await message.channel.send("> Error:そのIDのカテゴリーは存在しません。")
            return
        await message.channel.send("> 指定カテゴリー内の全チャンネルの期限を確認します。")
        count = 0
        print("-----check <{}> -----".format(str(category.id)))
        for chan in category.channels:
            last = await chan.history(limit=1).flatten()
            if not last:
                print("Continue <{}>".format(str(chan.id)))
                continue
            last_time = last[0].created_at
            now = datetime.datetime.now()
            s = now - last_time
            day = s.days
            if day > 30:
                await message.channel.send("> {}の有効期限が切れています。削除してください。".format(chan.mention))
                count += 1
                print("Found <{}>".format(chan.id))
            else:
                print("Continue <{}>".format(str(chan.id)))

        await message.channel.send("> 期限切れチャンネルが {} 個見つかりました".format(str(count)))
        print("-----end check <{}> -----".format(str(category.id)))
    elif len(sliced) == 1:
        category = message.channel.category
        if not category:
            await message.channel.send("> Error:発言チャンネルはカテゴリーの中に入っていません。")
            return
        await message.channel.send("> 指定カテゴリー内の全チャンネルの期限を確認します。")
        count = 0
        print("-----check <{}> -----".format(str(category.id)))
        for chan in category.channels:
            last = await chan.history(limit=1).flatten()
            if not last:
                print("Continue <{}>".format(str(chan.id)))
                continue
            last_time = last[0].created_at
            now = datetime.datetime.now()
            s = now - last_time
            day = s.days
            if day > 30:
                await message.channel.send("> {}の有効期限が切れています。削除してください。".format(chan.mention))
                count += 1
                print("Found <{}>".format(chan.id))
            else:
                print("Continue <{}>".format(str(chan.id)))

        await message.channel.send("> 期限切れチャンネルが {} 個見つかりました".format(str(count)))
        print("-----end check <{}> -----".format(str(category.id)))
    else:
        message.channel.send("Error:引数が多すぎます。")
        return

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("fr//"):
        if message.content == "fr//help":
            await help(message)
        elif message.content.startswith("fr//check"):
            await check(message)

client.run(config["TOKEN"])