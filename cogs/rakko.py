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
        self.file_path_chunithm = "songs_data_chunithm.json"
        self.file_path_ongeki = "songs_data_ongeki.json"
        
        self.songs_cache_chunithm = []
        self.songs_cache_ongeki = []
        
        self.load_all_songs()

    def load_all_songs(self):
        """ローカルJSONファイルからデータを読み込んでキャッシュする"""
        if os.path.exists(self.file_path_chunithm):
            try:
                with open(self.file_path_chunithm, "r", encoding="utf-8") as f:
                    self.songs_cache_chunithm = json.load(f)
                print(f"【成功】OdaiCog:「{self.file_path_chunithm}」から{len(self.songs_cache_chunithm)}件のデータを読み込みました。")
            except Exception as e:
                print(f"【エラー】{self.file_path_chunithm} の読み込みに失敗: {e}")
                self.songs_cache_chunithm = []
        else:
            print(f"【警告】{self.file_path_chunithm} が見つかりません。")

        if os.path.exists(self.file_path_ongeki):
            try:
                with open(self.file_path_ongeki, "r", encoding="utf-8") as f:
                    self.songs_cache_ongeki = json.load(f)
                print(f"【成功】OdaiCog:「{self.file_path_ongeki}」から{len(self.songs_cache_ongeki)}件のデータを読み込みました。")
            except Exception as e:
                print(f"【エラー】{self.file_path_ongeki} の読み込みに失敗: {e}")
                self.songs_cache_ongeki = []
        else:
            print(f"【警告】{self.file_path_ongeki} が見つかりません。")

    def _match_level(self, actual_const, target_level_str: str, game_type: str) -> bool:
        """レベル・定数の判定（レベル0対応版）"""
        try:
            const = float(actual_const)
            if const < 0:
                return False
                
            const_int = int(round(const * 10))
            target = target_level_str.strip()

            if '.' in target:
                target_int = int(round(float(target) * 10))
                return const_int == target_int

            elif target.endswith('+'):
                base_lv = int(target[:-1])
                if game_type == "chunithm":
                    return (base_lv * 10 + 5) <= const_int < (base_lv + 1) * 10
                else:
                    return (base_lv * 10 + 7) <= const_int < (base_lv + 1) * 10

            else:
                base_lv = int(target)
                if game_type == "chunithm":
                    return (base_lv * 10) <= const_int < (base_lv * 10 + 5)
                else:
                    return (base_lv * 10) <= const_int < (base_lv * 10 + 7)

        except (ValueError, TypeError, OverflowError):
            return False

    # スラッシュコマンド（/rakko）の定義
    @app_commands.command(name="rakko", description="指定したレベルからランダムで3曲選出")
    # 🌟 describeの中身を調整し、大文字で表示されるようにしています
    @app_commands.describe(
        game_type="機種（ゲーム）を選択してください",
        level="レベルを指定してください (例: 14, 14+, 14.2)",
        exclude_expert="EXPERT(EXP)を除外する場合は True を選択",
        exclude_master="MASTER(MAS)を除外する場合は True を選択",
        exclude_ultima_lunatic="ULTIMA(ULT) / LUNATIC(LUN)を除外する場合は True を選択"
    )
    @app_commands.choices(
        game_type=[
            app_commands.Choice(name="チュウニズム", value="chunithm"),
            app_commands.Choice(name="オンゲキ", value="ongeki")
        ]
    )
    async def odai(
        self, 
        interaction: discord.Interaction, 
        game_type: str, 
        level: str, 
        exclude_expert: bool = False, # 🌟 Discordの仕様に合わせ小文字に修正
        exclude_master: bool = False, 
        exclude_ultima_lunatic: bool = False
    ):
        await interaction.response.defer()
        
        try:
            if game_type == "chunithm":
                target_cache = self.songs_cache_chunithm
                game_title = "チュウニズム"
            else:
                target_cache = self.songs_cache_ongeki
                game_title = "オンゲキ"

            if not target_cache:
                await interaction.followup.send(f"選択された「{game_title}」の楽曲データが読み込まれていません。", ephemeral=True)
                return

            filtered_items = []

            for song in target_cache:
                meta = song.get('meta', {})
                data = song.get('data', {})
                
                for diff_name, diff_info in data.items():
                    actual_const = diff_info.get('const')
                    is_unknown = diff_info.get('is_const_unknown', 0)
                    
                    if actual_const is None:
                        continue

                    # レベル一致判定
                    if self._match_level(actual_const, level, game_type):
                        diff_upper = diff_name.upper()
                        
                        # 各難易度の除外チェック
                        if exclude_expert and "EXP" in diff_upper:
                            continue
                        if exclude_master and "MAS" in diff_upper:
                            continue
                        if exclude_ultima_lunatic and ("ULT" in diff_upper or "LUN" in diff_upper):
                            continue

                        # 文字列として「constの値(未確定)」の形にして保存する
                        if is_unknown == 1:
                            const_display = f"{actual_const}(未確定)"
                        else:
                            const_display = str(actual_const)

                        filtered_items.append({
                            'meta': meta,
                            'diff_name': diff_name,
                            'const': const_display
                        })

            if len(filtered_items) < 3:
                excludes = []
                if exclude_expert: excludes.append("EXP除外")
                if exclude_master: excludes.append("MAS除外")
                if exclude_ultima_lunatic: excludes.append("ULT/LUN除外")
                ex_str = f" ({', '.join(excludes)})" if excludes else ""
                
                await interaction.followup.send(
                    f"【{game_title}】レベル「{level}」{ex_str}の楽曲が3曲以上見つかりませんでした。（{len(filtered_items)}曲）", 
                    ephemeral=True
                )
                return

            chosen_items = random.sample(filtered_items, 3)

            img_path = "images/rakko.png"
            if not os.path.exists(img_path):
                await interaction.followup.send("画像ファイルが見つかりません。", ephemeral=True)
                return

            discord_file = discord.File(img_path, filename="rakko.png")

            embed = discord.Embed(title=f"🎵 {game_title}のお題はこれだッ 🎵", color=discord.Color.gold())
            
            status_list = []
            if exclude_expert: status_list.append("EXP除外")
            if exclude_master: status_list.append("MAS除外")
            if exclude_ultima_lunatic: status_list.append("ULT/LUN除外")
            status_desc = f" ({', '.join(status_list)})" if status_list else " (全難易度対象)"
            
            embed.description = f"対象レベル: **Level {level}**{status_desc}\n強く、なれッ...！"
            embed.set_image(url="attachment://rakko.png")

            for i, item in enumerate(chosen_items, 1):
                meta = item['meta']
                embed.add_field(
                    name=f"{i}曲目: {meta.get('title', 'Unknown')}",
                    value=f"アーティスト: {meta.get('artist', 'Unknown')}\n難易度: {item['diff_name']}\n譜面定数: {item['const']}",
                    inline=False
                )

            await interaction.followup.send(embed=embed, file=discord_file)

        except Exception as e:
            import traceback
            print(f"エラーが発生しました: {e}")
            print(traceback.format_exc())
            try:
                await interaction.followup.send(f"内部エラーが発生しました。\n```{str(e)[:1800]}```", ephemeral=True)
            except:
                pass

    @app_commands.command(name="reload_songs_file", description="【管理者用】すべてのJSONファイルを読み込み直します。")
    async def reload_songs_file(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.load_all_songs()
        
        msg = f"ローカルファイルからデータを再読み込みしました。\n"
        msg += f"・チュウニズム: 計 {len(self.songs_cache_chunithm)} 曲\n"
        msg += f"・オンゲキ: 計 {len(self.songs_cache_ongeki)} 曲"
        await interaction.followup.send(msg, ephemeral=True)

    @odai.error
    async def odai_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        import traceback
        print("❌【スラッシュコマンド内部でエラーが発生しました】")
        traceback.print_exception(type(error), error, error.__traceback__)
        
        error_text = f"⚠️ コマンドの実行中にエラーが発生しました:\n```python\n{error}\n```"
        try:
            await interaction.followup.send(error_text, ephemeral=True)
        except:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(OdaiCog(bot))
