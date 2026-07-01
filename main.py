import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
import asyncio
from dotenv import load_dotenv

# 1. 環境変数の読み込み (.envファイルの場所を指定)
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, 'donttouch.env')
load_dotenv(dotenv_path)

# 2. 接続に必要なオブジェクト（インテント）の設定
intents = discord.Intents.default()
intents.message_content = True

# 3. スラッシュコマンド自動同期に対応したBotクラスの定義
class MyBot(commands.Bot):
    async def setup_hook(self):
        # cogsフォルダ内の各キャラクターのファイルを自動で一括読み込み
        for filename in os.listdir(os.path.join(current_dir, "cogs")):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        
        await self.tree.sync()

# 4. Botインスタンスの生成
bot = MyBot(command_prefix="/", intents=intents)

# 5. ログイン完了イベント
@bot.event
async def on_ready():
    print(f'{bot.user} として正常にログインしました。')

# 6. 常時起動と接続を開始するメイン関数
async def main():
    async with bot:
        # 常時起動用のWebサーバーを起動
        keep_alive()
        # 環境変数からトークンを読み込んでBotを起動
        await bot.start(os.getenv("DISCORD_TOKEN"))

# 7. プログラムの実行
if __name__ == "__main__":
    asyncio.run(main())
