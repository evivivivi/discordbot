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

    def _match_level(self, actual_const: float, target_level_str: str) -> bool:


        # 実際の「譜面定数（actual_const）」が、ユーザーの指定したレベル文字列と一致するか判定する
        target = target_level_str.strip()

        # パターン1: 小数点が含まれる指定の場合（例: "14.2"）
        if '.' in target:
            try:
                # 浮動小数点の誤差を防ぐため、一度文字列にしてから厳密に比較
                return f"{actual_const:.1f}" == f"{float(target):.1f}"
            except ValueError:
                return False

        # パターン2: 小数点を無視した大枠の指定（「+」が付く場合、例: "14+"） -> 定数が .5 ~ .9 の範囲か
        elif target.endswith('+'):
            try:
                base_lv = int(target[:-1])
                # 整数部分が一致しているか
                if math.floor(actual_const) != base_lv:
                    return False
                
                # 小数点第一位の数字を文字として直接抜き出す（誤差ゼロ）
                # 例: 14.5 -> "5" -> int("5") -> 5
                under_dot = int(str(f"{actual_const:.1f}").split('.')[1])
                return under_dot >= 5 # 5〜9ならTrue
            except ValueError:
                return False

        # パターン3: 小数点を無視した大枠の指定（無印の場合、例: "14"） -> 定数が .0 ~ .4 の範囲か
        else:
            try:
                base_lv = int(target)
                # 整数部分が一致しているか
                if math.floor(actual_const) != base_lv:
                    return False
                
                # 小数点第一位の数字を文字として直接抜き出す（誤差ゼロ）
                under_dot = int(str(f"{actual_const:.1f}").split('.')[1])
                return under_dot < 5 # 0〜4ならTrue
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
