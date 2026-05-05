import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
import asyncio



# 接続に必要なオブジェクトを生成
# 1. Intentsのインスタンスを作成（標準設定を読み込む）
intents = discord.Intents.default()

# 2. メッセージ内容を取得したい場合はここをTrueにする
intents.message_content = True

# 3. 
bot = commands.Bot(command_prefix="/", intents=intents)


# 起動時にcogsフォルダ内のファイルを読み込む
async def load_extensions():
    await bot.load_extension("cogs.usagi")

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')

async def main():
    keep_alive()
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

# 実行
asyncio.run(main())