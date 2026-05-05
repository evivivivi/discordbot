import discord
import os
import random
from keep_alive import keep_alive
import os

# ...（Botの設定など）...

usagi=["イ","ヤ","ハ","ウ","ラ","ツ","ル","プ"]

def generate_random_string():
    random_string = "".join(random.choice(usagi) for _ in range(random.randint(3,8)))
    return random_string



# 接続に必要なオブジェクトを生成
# 1. Intentsのインスタンスを作成（標準設定を読み込む）
intents = discord.Intents.default()

# 2. メッセージ内容を取得したい場合はここをTrueにする
intents.message_content = True

# 3. Clientを作成する際にintentsを渡す（ここがエラーの原因）
client = discord.Client(intents=intents)


# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/usagi':
        random_text = generate_random_string()
        await message.channel.send(random_text)

keep_alive() # Webサーバーを起動
client.run(os.getenv("DISCORD_TOKEN")) # 環境変数からトークンを読み込む