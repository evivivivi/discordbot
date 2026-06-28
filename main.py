import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
import asyncio
from dotenv import load_dotenv

# --- 【修正ポイント】.envの場所を確実に指定して読み込む ---
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, 'donttouch.env')
load_dotenv(dotenv_path)
# --------------------------------------------------------

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# 起動時にcogsフォルダ内のファイルを読み込む
async def load_extensions():
    for filename in os.listdir(os.path.join(current_dir, "cogs")):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')

async def main():
    keep_alive()
    async with bot:
        await load_extensions()
        # --- 【修正ポイント】ここを元の環境変数読み込みに戻す ---
        await bot.start(os.getenv("DISCORD_TOKEN"))

# 実行
asyncio.run(main())
