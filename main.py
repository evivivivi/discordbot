import discord
from keep_alive import keep_alive
import os

# ...（Botの設定など）...

keep_alive() # Webサーバーを起動
client.run(os.getenv("DISCORD_TOKEN")) # 環境変数からトークンを読み込む