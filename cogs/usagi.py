import discord
from discord.ext import commands
import random



class Usagi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.usagi_parts = ["イ","ヤ","ハ","ウ","ラ","ツ","ル","プ"]

    def generate_random_string(self):
        return "".join(random.choice(self.usagi_parts) for _ in range(random.randint(2, 6)))

    # メッセージ受信イベント
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content == 'うさぎ':
            file = discord.File("images/usagi.png")
            await message.channel.send(self.generate_random_string(),file=file)

# main.pyから呼び出すための準備
async def setup(bot):
    await bot.add_cog(Usagi(bot))