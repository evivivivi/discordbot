import discord
from discord.ext import commands
from discord import app_commands
import random
import os

class Momonga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.momonga_parts = [
            "褒めろッ", "慰めろッ", "ｷﾗｯ✨ｷﾗｯ✨✨", "ついにやったぞ…！", 
            "叱ってみろ", "ご苦労なこった", "イーヤー ヤダヤダ", "ﾋﾟｴｪ〜🥺ｳｴｪ〜😭", 
            "み～～て～～～～", "揺らせッ", "静かに泣くか", "やさし～く 撫でろッ", 
            "甘いものが食べたいんだよォーーーー！！！！", "ハフムシャッと食べるんだからさァ", 
            "ぜ～んぜん 「うまみ」がないぞッ..."
        ]

    def generate_random_momonga(self):
        return random.choice(self.momonga_parts)

    # 💡 --- スラッシュコマンド (/momonga) の定義 ---
    @app_commands.command(name="momonga", description="モモンガがランダムなセリフを叫びます。")
    async def momonga_shout(self, interaction: discord.Interaction):
        img_path = "images/momonga.png"
        img_name = "momonga.png"

        # 画像の存在チェック（エラー防止の安全ブレーキ）
        if not os.path.exists(img_path):
            await interaction.response.send_message(f"エラー: 画像「{img_path}」が見つかりません。", ephemeral=True)
            return

        file = discord.File(img_path, filename=img_name)
        
        # ランダムなセリフを取得
        message_content = self.generate_random_momonga()

        # ⬇️【変更】Embed（埋め込み）の作成
        embed = discord.Embed(
            title=f"🍑 {interaction.user.display_name} への一言",
            description=f"**{message_content}**",
            color=discord.Color.from_rgb(255, 192, 203) # モモンガっぽいピンク色に設定
        )
        # Embedに画像をセット
        embed.set_image(url=f"attachment://{img_name}")

        # ⬇️【変更】作成したEmbedとファイルを同時に送信
        await interaction.response.send_message(embed=embed, file=file)

async def setup(bot: commands.Bot):
    await bot.add_cog(Momonga(bot))
