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

@bot.event
async def on_message(message):
    # تجاهل رسائل البوت
    if message.author == bot.user:
        return
    
    # إذا كانت الرسالة تحتوي على "حمزه"
    if "حمزه" in message.content.lower():
        try:
            # البوت يكتب نقطة بس
            await message.channel.send("•")
            print(f"✅ كُتبت النقطة")
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
    
    await bot.process_commands(message)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ لا يوجد TOKEN في config.json")
