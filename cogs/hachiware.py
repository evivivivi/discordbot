import discord
from discord.ext import commands
from discord import app_commands
import random
import os

class Hachiware(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 💡 --- スラッシュコマンド (/hachiware) の定義 ---
    @app_commands.command(name="hachiware", description="ハチワレが今日の運勢を占ってくれます。")
    async def hachiware_fortune(self, interaction: discord.Interaction):
        # 運勢を決定
        fortunes = ["大吉", "中吉", "吉", "小吉", "凶", "大凶"]
        result = random.choice(fortunes)
        col = discord.Color.green()
        img_path = "images/hachiware.png"
        img_name = "hachiware.png"
        
        # 💡 message.author.mention を interaction.user.mention に変更
        if result == "大吉":
            msg = f"✨ {interaction.user.mention} おめでとう！それって最高じゃん！！"
        elif result == "中吉":
            msg = f"😄 {interaction.user.mention} 具なくてもさァ！！ おいしいよね チャリメラって！！"
        elif result == "吉":
            msg = f"🎵 {interaction.user.mention} でも これも... 「味」だよねっ"
        elif result == "小吉":
            msg = f"🤨 {interaction.user.mention} だいじょぶっ いつもなんとかなってるもん！！"
        elif result == "凶":
            msg = f"☔ {interaction.user.mention} ほんとに...つらかったらいいと思うッやめても..."
        else:
            msg = f"😥 {interaction.user.mention} だめそうだったらさー リタイアすればいいよね"

        # 画像の存在チェック
        if not os.path.exists(img_path):
            await interaction.response.send_message(f"エラー: 画像「{img_path}」が見つかりません。", ephemeral=True)
            return

        file = discord.File(img_path, filename=img_name)

        # --- 埋め込み（Embed）の作成 ---
        embed = discord.Embed(
            title=f"✨ {interaction.user.display_name} さんの運勢：{result}",
            description=msg,
            color=col
        )
        embed.set_image(url=f"attachment://{img_name}")

        # --- 結果を送信 ---
        await interaction.response.send_message(file=file, embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Hachiware(bot))
