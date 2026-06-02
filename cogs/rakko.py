import discord
from discord.ext import commands
import random

class Rakko(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.momonga_parts = ["褒めろッ","慰めろッ","ｷﾗｯ✨ｷﾗｯ✨✨","ついにやったぞ…！","叱ってみろ","ご苦労なこった","イーヤー ヤダヤダ","ﾋﾟｴｪ〜🥺ｳｴｪ〜😭","み～～て～～～～","揺らせッ","静かに泣くか","やさし～く 撫でろッ","甘いものが食べたいんだよォーーーー！！！！","ハフムシャッと食べるんだからさァ","ぜ～んぜん 「うまみ」がないぞッ..."]

    def generate_random_momonga(self):
        return random.choice(self.momonga_parts)

    # メッセージ受信イベント
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content == 'ラッコ':
            file = discord.File("images/momonga.png")
            await message.channel.send(self.generate_random_momonga(),file=file)

# main.pyから呼び出すための準備
async def setup(bot):
    await bot.add_cog(Momonga(bot))
