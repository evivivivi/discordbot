import discord
from discord.ext import commands
from discord import app_commands
import random
import os

class Usagi(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.usagi_parts = ["イ", "ヤ", "ハ", "ウ", "ラ", "ツ", "ル", "プ"]

    def generate_random_string(self):
        # 2文字から6文字のランダムな奇声を生成するロジック
        return "".join(random.choice(self.usagi_parts) for _ in range(random.randint(2, 6)))

    # 💡 --- スラッシュコマンド (/usagi) の定義 ---
    @app_commands.command(name="usagi", description="うさぎがランダムに奇声をあげます。")
    async def usagi_shout(self, interaction: discord.Interaction):
        img_path = "images/usagi.png"
        img_name = "usagi.png"

        # 画像の存在チェック（エラー防止の安全ブレーキ）
        if not os.path.exists(img_path):
            await interaction.response.send_message(f"エラー: 画像「{img_path}」が見つかりません。", ephemeral=True)
            return

        file = discord.File(img_path, filename=img_name)
        
        # ランダムな叫び声（例: 「ヤハ」「ウララ」など）を生成
        shout_content = self.generate_random_string()

        # 💡 Embed（埋め込み）の作成
        embed = discord.Embed(
            title=f"🐰 うさぎが{interaction.user.display_name} に放った言葉とは...！",
            description=f"# **{shout_content}**", # # を使うことで文字を大きく強調させています
            color=discord.Color.gold() # うさぎっぽい黄色に設定
        )
        # Embedに画像をセット
        embed.set_image(url=f"attachment://{img_name}")

        # 作成したEmbedとファイルを同時に送信
        await interaction.response.send_message(embed=embed, file=file)

async def setup(bot: commands.Bot):
    await bot.add_cog(Usagi(bot))
