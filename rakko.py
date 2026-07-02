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

    def _match_level(self, actual_const: float, target_level_str: str) -> bool:

        target = target_level_str.strip()

        # 🌟 実際の譜面定数を10倍して「四捨五入した整数」にする (例: 14.5 -> 145 / 14.2 -> 142)
        # round(..., 1)ではなく、int(round(x * 10)) とすることで小数のゴミを完全に消滅させます
        const_int = int(round(actual_const * 10))

        # ----------------------------------------------------
        # パターン1: 小数点指定 (例: "14.2")
        # ----------------------------------------------------
        if '.' in target:
            try:
                # 入力されたターゲット（例: "14.2"）も10倍の整数（142）にする
                target_int = int(round(float(target) * 10))
                return const_int == target_int
            except ValueError:
                return False

        # ----------------------------------------------------
        # パターン2: プラス指定 (例: "14+") -> 定数が 14.5 〜 14.9 (145 〜 149) の範囲か
        # ----------------------------------------------------
        elif target.endswith('+'):
            try:
                base_lv = int(target[:-1])
                # 14+ なら、145 以上 かつ 150 未満 かどうかを整数で調べる（誤差ゼロ）
                min_val = base_lv * 10 + 5  # 例: 14 * 10 + 5 = 145
                max_val = (base_lv + 1) * 10 # 例: 15 * 10 = 150
                return min_val <= const_int < max_val
            except ValueError:
                return False

        # ----------------------------------------------------
        # パターン3: 整数指定 (例: "14") -> 定数が 14.0 〜 14.4 (140 〜 144) の範囲か
        # ----------------------------------------------------
        else:
            try:
                base_lv = int(target)
                # 14 無印なら、140 以上 かつ 145 未満 かどうかを整数で調べる（誤差ゼロ）
                min_val = base_lv * 10       # 例: 14 * 10 = 140
                max_val = base_lv * 10 + 5   # 例: 14 * 10 + 5 = 145
                return min_val <= const_int < max_val
            except ValueError:
                return False

    # スラッシュコマンド（/rakko）の定義
    @app_commands.command(name="rakko", description="指定したレベル（譜面定数）からランダムで3曲選出します。小数点指定も可能です。")
    @app_commands.describe(level="レベルを指定してください (例: 14, 14+, 14.2)")
    async def odai(self, interaction: discord.Interaction, level: str):
        if not self.songs_cache:
            await interaction.response.send_message("楽曲データが読み込まれていません。管理者に確認してください。", ephemeral=True)
            return

        filtered_items = []
        
        # メモリ内のデータから条件に合う楽曲を抽出
        for song in self.songs_cache:
            meta = song.get('meta', {})
            data = song.get('data', {})
            
            for diff_name, diff_info in data.items():
                actual_const = diff_info.get('const')
                is_unknown = diff_info.get('is_const_unknown', 0) # 未解析フラグ（無い場合は0）
                
                # 💡【追加条件】定数が存在し、0より大きく、かつ未解析フラグが 1 ではない場合のみ許可
                if actual_const is not None and float(actual_const) > 0 and is_unknown != 1:
                    # その上でユーザーの指定したレベルと合致するか判定
                    if self._match_level(float(actual_const), level):
                        filtered_items.append({
                            'meta': meta,
                            'diff_name': diff_name,
                            'const': actual_const
                        })

        if len(filtered_items) < 3:
            await interaction.response.send_message(f"レベル「{level}」の楽曲が3曲以上見つかりませんでした。（候補: {len(filtered_items)}曲）", ephemeral=True)
            return

        # ランダム選出
        chosen_items = random.sample(filtered_items, 3)

        # ラッコの画像設定
        img_path = "images/rakko.png"
        img_name = "rakko.png"
        
        if os.path.exists(img_path):
            discord_file = discord.File(img_path, filename=img_name)
        else:
            await interaction.response.send_message(f"エラー: 画像ファイル「{img_path}」が見つかりません。フォルダを確認してください。", ephemeral=True)
            return

        # Embedの作成
        embed = discord.Embed(title="🎵 お題はこれだッ 🎵", color=discord.Color.gold())
        embed.description = f"対象レベル: **Level {level}**\n強く、なれッ...！"
        embed.set_image(url=f"attachment://{img_name}")

        for i, item in enumerate(chosen_items, 1):
            meta = item['meta']
            embed.add_field(
                name=f"{i}曲目: {meta.get('title', 'Unknown')}",
                value=f"アーティスト: {meta.get('artist', 'Unknown')}\n難易度: {item['diff_name']}",
                inline=False
            )

        # 結果を送信
        await interaction.response.send_message(embed=embed, file=discord_file)

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
