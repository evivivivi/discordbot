import discord
from discord.ext import commands, tasks
import random
import os
import datetime

# 設定項目
CHANNEL_ID = 1501416156672823356  # 結果を投稿したいテキストチャンネルのID
ROLE_ID = 1529115591695142992     # 占い対象にしたい「ロール（役職）」のID

# 時間の設定（日本時間 00:25 ➔ UTC 15:25）
EXECUTE_TIME = datetime.time(
    hour=23, 
    minute=0, 
    second=0, 
    tzinfo=datetime.timezone.utc
)


class DailyFortune(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_fortune.start()  # Bot起動時に自動実行タスクを開始

    def cog_unload(self):
        self.daily_fortune.cancel()  # Cogがアンロードされたらタスクを停止

    # 運勢のメッセージを生成するロジック
    def generate_fortune_message(self, user: discord.Member):
        fortunes = ["大吉", "中吉", "吉", "小吉", "凶", "大凶"]
        result = random.choice(fortunes)
        
        if result == "大吉":
            msg = f"✨ {user.mention} おめでとう！それって最高じゃん！！"
        elif result == "中吉":
            msg = f"😄 {user.mention} 具なくてもさァ！！ おいしいよね チャリメラって！！"
        elif result == "吉":
            msg = f"🎵 {user.mention} でも これも... 「味」だよねっ"
        elif result == "小吉":
            msg = f"🤨 {user.mention} だいじょぶっ いつもなんとかなってるもん！！"
        elif result == "凶":
            msg = f"☔ {user.mention} ほんとに...つらかったらいいと思うッやめても..."
        else:
            msg = f"😥 {user.mention} だめそうだったらさー リタイアすればいいよね"
            
        return result, msg

    @tasks.loop(time=EXECUTE_TIME)
    async def daily_fortune(self):
        print("[INFO] Timer triggered")
        await self.bot.wait_until_ready()
        
        # 投稿先チャンネルを取得
        channel = self.bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"[ERROR] Channel ID ({CHANNEL_ID}) not found")
            return
        print(f"[SUCCESS] Channel found: #{channel.name}")

        img_path = "images/hachiware.png"
        if not os.path.exists(img_path):
            print(f"[ERROR] Image path ({img_path}) does not exist")
            return

        # サーバーとロールを取得
        guild = channel.guild
        
        # 最新のメンバー名簿をダウンロードして同期
        try:
            print("[INFO] Fetching latest guild members...")
            async for member in guild.fetch_members(limit=None):
                pass  # キャッシュ更新のために全メンバーをループに通す
            print("[SUCCESS] Guild members sync completed")
        except Exception as e:
            print(f"[ERROR] Failed to fetch members: {e}")
            return

        role = guild.get_role(ROLE_ID)
        if not role:
            print(f"[ERROR] Role ID ({ROLE_ID}) not found")
            return
        print(f"[SUCCESS] Role found: @{role.name}")

        # ロールを持っているメンバーを全員取得（Botは除外）
        members = [m for m in role.members if not m.bot]
        print(f"[INFO] Target members count: {len(members)}")
        
        if not members:
            print("[WARN] No members found with the specified role. Skipping execution")
            return

        # 1つのEmbedに全員分をまとめる
        embed = discord.Embed(
            title="ハチワレの運勢占い",
            description="今日の運勢を占ったよッ！",
            color=discord.Color.green()
        )

        # メンバー一人ずつ占ってフィールド（枠）を追加
        for member in members:
            result, msg = self.generate_fortune_message(member)
            embed.add_field(
                name=f"{member.display_name} さん ➔ 【{result}】",
                value=msg,
                inline=False
            )
            print(f"[INFO] Fortune assigned for {member.display_name}")

        # ハチワレの画像をセットして送信
        embed.set_image(url="attachment://hachiware.png")
        file = discord.File(img_path, filename="hachiware.png")
        
        await channel.send(file=file, embed=embed)
        print("[SUCCESS] Fortune message sent successfully")


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyFortune(bot))
