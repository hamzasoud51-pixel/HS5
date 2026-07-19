import discord
from discord.ext import commands
import json
import os

# تحميل الإعدادات
def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()
TOKEN = config.get('TOKEN', '')

# إنشاء البوت
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ البوت شغّال: {bot.user}")
    # كتابة نقطة واحدة دلوقتي
    await send_dot_now()

async def send_dot_now():
    """كتابة نقطة في أول قناة"""
    try:
        # البحث عن أول قناة نصية
        for guild in bot.guilds:
            for channel in guild.text_channels:
                try:
                    await channel.send("•")
                    print(f"✅ تم كتابة النقطة في {guild.name} - {channel.name}")
                    return
                except:
                    pass
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ لا يوجد TOKEN في config.json")
