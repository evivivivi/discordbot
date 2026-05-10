import discord
from discord.ext import commands
import random

class Hachiware(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # インデントを修正

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == 'ハチワレ':
            # 運勢を決定
            fortunes = ["大吉", "中吉", "吉", "小吉", "凶", "大凶"]
            result = random.choice(fortunes)
            col = discord.Color.green()
            img_path = "images/hachiware.png"
            img_name = "hachiware.png" # ここを定義
            
            # 分岐処理（インデントをすべて半角スペース4つに統一）
            if result == "大吉":
                msg = f"✨ {message.author.mention} おめでとう！それって最高じゃん！！"
            elif result == "中吉":
                msg = f"😄 {message.author.mention} 具なくてもさァ！！ おいしいよね チャリメラって！！"
            elif result == "吉":
                msg = f"🎵 {message.author.mention} でも これも... 「味」だよねっ"
            elif result == "小吉":
                msg = f"🤨 {message.author.mention} だいじょぶっ いつもなんとかなってるもん！！"
            elif result == "凶":
                msg = f"☔ {message.author.mention} ほんとに...つらかったらいいと思うッやめても..."
            else:
                msg = f"😥 {message.author.mention} だめそうだったらさー リタイアすればいいよね"

            # --- 埋め込み（Embed）の作成 ---
            embed = discord.Embed(
                title=f"✨ {message.author.display_name} さんの運勢：{result}",
                description=msg,
                color=col
            )
            
            # 画像の設定
            file = discord.File(img_path, filename=img_name)
            embed.set_image(url=f"attachment://{img_name}")

            # --- 送信（これだけで画像と埋め込みが一緒に届きます） ---
            await message.channel.send(file=file, embed=embed)

async def setup(bot):
    await bot.add_cog(Hachiware(bot))
