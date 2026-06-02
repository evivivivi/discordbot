import discord
from discord.ext import commands
import random

class Chiikawa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 1. まず「レアリティ自体の確率」を定義（合計100になるようにする）
        self.rarity_weights = {
            "N": 70,   # N全体で70%
            "R": 24,   # R全体で20%
            "SR": 5,   # SR全体で8%
            "UR": 1    # UR全体で2%
        }
        
        # 2. レアリティごとのアイテムリスト（何個追加してもOK！）
        self.gacha_pool = {
            "N": [
                "🌱 普通の草", 
                "🌱 触れるとかぶれちゃう金色の草", 
                "🌱 かたい草",
                "🌾 イネ科の草",
                "🍂 落ち葉",
                "☘️ クローバー",
                "🐜 アリ",
                "🪱 ミミズ",
                "🐛 毛虫",
                "🌱 枯れた草"
            ],
            "R": [
                "🍄 ちょっと大きいキノコ", 
                "🌱 長くてしぶとい根っこ", 
                "🍙 湧き出たごはん",
                "🥀 しおれた花",
                "🦗 バッタ",
                "🐞 てんとう虫",
                "🐌 カタツムリ",
                "🕷️ クモ"
            ],
            "SR": [
                "🥕 マンドラゴラ", 
                "🍬 小さいアメ",
                "🦋 きれいなチョウチョ",
                "☕ 「缶コーヒーをもらった！」",
                "🍀 四葉のクローバー"
            ],
            "UR": [
                "☠️ 絶対にむしっちゃいけない草", 
                "🪙 異国のコイン",
                "🖼️ 無題の絵画"
            ]
        }

    # ガチャを引く共通処理（2段階）
    def pull_gacha(self):
        # ステップ1：レアリティを確率で選ぶ
        rarities = list(self.rarity_weights.keys())
        weights = list(self.rarity_weights.values())
        chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
        
        # ステップ2：選ばれたレアリティのリストから等確率で1個選ぶ
        item_list = self.gacha_pool[chosen_rarity]
        chosen_item_name = random.choice(item_list)
        
        # 結果を辞書にして返す
        return {"name": chosen_item_name, "rarity": chosen_rarity}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # --- 単発ガチャ ---
        if message.content == 'ちいかわ':
            result = self.pull_gacha()
            
            col = discord.Color.green() if result["rarity"] in ["N", "R"] else discord.Color.gold()
            img_path = "images/chiikawa.png"
            img_name = "chiikawa.png" # ここを定義

            
            embed = discord.Embed(
                title=f"🌱 {message.author.display_name} さんの草むしり結果",
                description=f"むしったもの：**{result['name']}** (レア度: {result['rarity']})",
                color=col
            )
            # 画像の設定
            file = discord.File(img_path, filename=img_name)
            embed.set_image(url=f"attachment://{img_name}")
           
            await message.channel.send(file=file,embed=embed)

        # --- 10連ガチャ ---
        elif message.content == 'ちいかわ10':
            results = [self.pull_gacha() for _ in range(10)]
            
            text_list = []
            img_path = "images/chiikawa.png"
            img_name = "chiikawa.png" # ここを定義

            
            for i, res in enumerate(results, 1):
                text_list.append(f"{i}回目：{res['name']} [{res['rarity']}]")

            embed = discord.Embed(
                title=f"🚜 {message.author.display_name} さんの10連草むしり結果",
                description="\n".join(text_list),
                color=discord.Color.blue()
            )
            
          # 画像の設定
            file = discord.File(img_path, filename=img_name)
            embed.set_image(url=f"attachment://{img_name}")
           
            await message.channel.send(file=file,embed=embed)


async def setup(bot):
    await bot.add_cog(Chiikawa(bot))