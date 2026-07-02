import discord
from discord.ext import commands
from discord import app_commands
import json
import math
import random
import os

class OdaiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_filepath = "songs_data.json" # 読み込むJSONファイル名
        self.songs_cache = []
        
        # Bot起動（コグ読み込み）時にローカルファイルからデータをロード
        self.load_songs_from_file()

    def load_songs_from_file(self):
        """ローカルのJSONファイルからデータを読み込んでメモリにキャッシュする"""
        if os.path.exists(self.data_filepath):
            try:
                with open(self.data_filepath, "r", encoding="utf-8") as f:
                    self.songs_cache = json.load(f)
                print(f"【成功】OdaiCog:「{self.data_filepath}」から{len(self.songs_cache)}件のデータを読み込みました。")
            except Exception as e:
                print(f"【エラー】ファイルの読み込みに失敗しました: {e}")
                self.songs_cache = []
        else:
            print(f"【警告】{self.data_filepath} が見つかりません。データを配置してください。")
            self.songs_cache = []

def _match_level(self, actual_const, target_level_str: str) -> bool:
    """actual_constはint/floatのどちらもあり得る"""
    try:
        # 確実にfloatに変換
        const = float(actual_const)
        if const <= 0:
            return False
            
        const_int = int(round(const * 10))
        target = target_level_str.strip()

        if '.' in target:
            # 14.1 など
            target_int = int(round(float(target) * 10))
            return const_int == target_int

        elif target.endswith('+'):
            # 14+
            base_lv = int(target[:-1])
            return (base_lv * 10 + 5) <= const_int < (base_lv + 1) * 10

        else:
            # 14（14.0〜14.4）
            base_lv = int(target)
            return (base_lv * 10) <= const_int < (base_lv * 10 + 5)

    except (ValueError, TypeError, OverflowError):
        return False

@app_commands.command(name="rakko", description="指定したレベルからランダムで3曲選出")
@app_commands.describe(level="レベルを指定してください (例: 14, 14+, 14.2)")
async def odai(interaction: discord.Interaction, level: str):
    await interaction.response.defer()  # ← これを最初に呼ぶ！タイムアウト対策
    
    try:
        if not self.songs_cache:
            await interaction.followup.send("楽曲データが読み込まれていません。", ephemeral=True)
            return

        filtered_items = []

        for song in self.songs_cache:
            meta = song.get('meta', {})
            data = song.get('data', {})
            
            for diff_name, diff_info in data.items():
                actual_const = diff_info.get('const')
                is_unknown = diff_info.get('is_const_unknown', 0)
                
                if actual_const is None:
                    continue

                if is_unknown == 1:
                    continue


                if self._match_level(actual_const, level):
                    filtered_items.append({
                        'meta': meta,
                        'diff_name': diff_name,
                        'const': actual_const
                    })

        if len(filtered_items) < 3:
            await interaction.followup.send(
                f"レベル「{level}」の楽曲が3曲以上見つかりませんでした。（{len(filtered_items)}曲）", 
                ephemeral=True
            )
            return

        chosen_items = random.sample(filtered_items, 3)

        # 画像処理...
        img_path = "images/rakko.png"
        if not os.path.exists(img_path):
            await interaction.followup.send("画像ファイルが見つかりません。", ephemeral=True)
            return

        discord_file = discord.File(img_path, filename="rakko.png")

        embed = discord.Embed(title="🎵 お題はこれだッ 🎵", color=discord.Color.gold())
        embed.description = f"対象レベル: **Level {level}**\n強く、なれッ...！"
        embed.set_image(url="attachment://rakko.png")

        for i, item in enumerate(chosen_items, 1):
            meta = item['meta']
            embed.add_field(
                name=f"{i}曲目: {meta.get('title', 'Unknown')}",
                value=f"アーティスト: {meta.get('artist', 'Unknown')}\n難易度: {item['diff_name']}",
                inline=False
            )

        await interaction.followup.send(embed=embed, file=discord_file)

    except Exception as e:
        import traceback
        error_msg = f"エラーが発生しました: {e}"
        print(error_msg)
        print(traceback.format_exc())
        try:
            await interaction.followup.send(f"内部エラーが発生しました。\n```{str(e)[:1800]}```", ephemeral=True)
        except:
            pass

    # 管理者用ファイル再読込スラッシュコマンド（/reload_songs_file）
    @app_commands.command(name="reload_songs_file", description="【管理者用】保存されているJSONファイルを読み込み直します。")
    async def reload_songs_file(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.load_songs_from_file()
        if self.songs_cache:
            await interaction.followup.send(f"ローカルファイルからデータを再読み込みしました。（計 {len(self.songs_cache)} 曲）", ephemeral=True)
        else:
            await interaction.followup.send("データの再読み込みに失敗しました。ファイルが存在するか確認してください。", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(OdaiCog(bot))
