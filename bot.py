import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
import asyncio
import logging

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل الإعدادات من config.json
def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()
TOKEN = config.get('TOKEN', '')
PREFIX = config.get('PREFIX', '!')

# إنشاء البوت مع إعدادات استقرار
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix=PREFIX, 
    intents=intents,
    heartbeat_timeout=120,  # انتظر 120 ثانية قبل قطع الاتصال
)

# متغيرات العد
bot.uptime = None
bot.command_count = 0

# ===== مهام دورية =====

@tasks.loop(minutes=5)
async def keep_alive():
    """مهمة دورية للحفاظ على البوت حياً كل 5 دقائق"""
    try:
        logger.info(f"✅ البوت حي - {datetime.now().strftime('%H:%M:%S')}")
        # تحديث حالة البوت
        await bot.change_presence(
            activity=discord.Game(name=f"مساعدة مع {PREFIX}help"),
            status=discord.Status.online
        )
    except Exception as e:
        logger.error(f"❌ خطأ في keep_alive: {e}")

@tasks.loop(hours=1)
async def health_check():
    """فحص صحة البوت كل ساعة"""
    try:
        logger.info(f"🏥 فحص صحة البوت - عدد الأوامر: {bot.command_count}")
    except Exception as e:
        logger.error(f"❌ خطأ في health_check: {e}")

# ===== الأحداث =====

@bot.event
async def on_ready():
    """يتم تنفيذه عندما يكون البوت جاهز"""
    bot.uptime = datetime.now()
    print(f"""
    ╔════════════════════════════════════╗
    ║  🤖 البوت جاهز للعمل               ║
    ║  👤 الاسم: {bot.user}
    ║  🆔 ID: {bot.user.id}
    ║  ⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}
    ║  📊 عدد السيرفرات: {len(bot.guilds)}
    ╚════════════════════════════════════╝
    """)
    
    # بدء المهام الدورية
    if not keep_alive.is_running():
        keep_alive.start()
        logger.info("🔄 تم بدء مهمة keep_alive")
    
    if not health_check.is_running():
        health_check.start()
        logger.info("🔄 تم بدء مهمة health_check")

@bot.event
async def on_message(message):
    """يتم تنفيذه عند استقبال رسالة"""
    # تجاهل رسائل البوت
    if message.author == bot.user:
        return
    
    try:
        # معالجة الأوامر
        await bot.process_commands(message)
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}")

@bot.event
async def on_disconnect():
    """يتم تنفيذه عند قطع الاتصال"""
    logger.warning("⚠️ تم قطع الاتصال بـ Discord!")

@bot.event
async def on_resumed():
    """يتم تنفيذه عند استئناف الاتصال"""
    logger.info("✅ تم استئناف الاتصال بـ Discord!")

# ===== الأوامر =====

@bot.command(name='hello', help='تحية بسيطة')
async def hello(ctx):
    """أمر التحية"""
    try:
        embed = discord.Embed(
            title="👋 مرحباً!",
            description=f"أهلاً وسهلاً {ctx.author.mention}!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في hello: {e}")
        await ctx.send("❌ حدث خطأ!")

@bot.command(name='ping', help='اختبار سرعة الاتصال')
async def ping(ctx):
    """اختبار البينج"""
    try:
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Ping",
            description=f"سرعة الاتصال: **{latency}ms**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في ping: {e}")
        await ctx.send("❌ حدث خطأ!")

@bot.command(name='uptime', help='مدة عمل البوت')
async def uptime(ctx):
    """عرض مدة عمل البوت"""
    try:
        if bot.uptime:
            delta = datetime.now() - bot.uptime
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60
            
            embed = discord.Embed(
                title="⏱️ مدة عمل البوت",
                description=f"**{delta.days}** يوم، **{hours}** ساعة، **{minutes}** دقيقة، **{seconds}** ثانية",
                color=discord.Color.purple()
            )
            await ctx.send(embed=embed)
            bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في uptime: {e}")
        await ctx.send("❌ حدث خطأ!")

@bot.command(name='info', help='معلومات عن السيرفر')
async def info(ctx):
    """معلومات عن السيرفر"""
    try:
        guild = ctx.guild
        embed = discord.Embed(
            title=f"ℹ️ معلومات {guild.name}",
            description=f"معلومات عن السيرفر الحالي",
            color=discord.Color.purple()
        )
        embed.add_field(name="👥 عدد الأعضاء", value=guild.member_count, inline=True)
        embed.add_field(name="📅 تاريخ الإنشاء", value=guild.created_at.strftime('%Y-%m-%d'), inline=True)
        embed.add_field(name="🆔 معرف السيرفر", value=guild.id, inline=True)
        embed.add_field(name="📊 عدد الأوامر", value=bot.command_count, inline=True)
        await ctx.send(embed=embed)
        bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في info: {e}")
        await ctx.send("❌ حدث خطأ!")

@bot.command(name='user', help='معلومات عنك')
async def user_info(ctx):
    """معلومات عن المستخدم"""
    try:
        user = ctx.author
        embed = discord.Embed(
            title=f"👤 معلومات {user.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="📝 الاسم", value=user.name, inline=True)
        embed.add_field(name="🆔 المعرف", value=user.id, inline=True)
        embed.add_field(name="📅 انضم في", value=user.created_at.strftime('%Y-%m-%d'), inline=True)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        await ctx.send(embed=embed)
        bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في user_info: {e}")
        await ctx.send("❌ حدث خطأ!")

@bot.command(name='echo', help='تكرار الرسالة')
async def echo(ctx, *, message):
    """تكرار الرسالة المرسلة"""
    try:
        embed = discord.Embed(
            title="🔊 Echo",
            description=message,
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في echo: {e}")
        await ctx.send("❌ حدث خطأ!")

@bot.command(name='help', help='عرض جميع الأوامر')
async def help_command(ctx):
    """عرض قائمة الأوامر"""
    try:
        embed = discord.Embed(
            title="📚 قائمة الأوامر",
            description=f"استخدم `{PREFIX}command` لتنفيذ الأمر",
            color=discord.Color.gold()
        )
        embed.add_field(name=f"{PREFIX}hello", value="تحية بسيطة", inline=False)
        embed.add_field(name=f"{PREFIX}ping", value="اختبار سرعة الاتصال", inline=False)
        embed.add_field(name=f"{PREFIX}info", value="معلومات عن السيرفر", inline=False)
        embed.add_field(name=f"{PREFIX}user", value="معلومات عنك", inline=False)
        embed.add_field(name=f"{PREFIX}echo", value="تكرار الرسالة", inline=False)
        embed.add_field(name=f"{PREFIX}uptime", value="مدة عمل البوت", inline=False)
        embed.add_field(name=f"{PREFIX}status", value="حالة البوت", inline=False)
        embed.set_footer(text=f"لـ مساعدة أكثر: {PREFIX}help")
        await ctx.send(embed=embed)
        bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في help: {e}")
        await ctx.send("❌ حدث خطأ!")

@bot.command(name='status', help='حالة البوت')
async def status(ctx):
    """حالة البوت الحالية"""
    try:
        embed = discord.Embed(
            title="📊 حالة البوت",
            color=discord.Color.green()
        )
        embed.add_field(name="🟢 الحالة", value="**تشغيل عادي**", inline=False)
        embed.add_field(name="📈 عدد الأوامر", value=bot.command_count, inline=True)
        embed.add_field(name="🏓 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="📡 السيرفرات", value=len(bot.guilds), inline=True)
        embed.add_field(name="👥 المستخدمون", value=sum(g.member_count for g in bot.guilds), inline=True)
        await ctx.send(embed=embed)
        bot.command_count += 1
    except Exception as e:
        logger.error(f"❌ خطأ في status: {e}")
        await ctx.send("❌ حدث خطأ!")

# ===== معالجة الأخطاء =====

@bot.event
async def on_command_error(ctx, error):
    """معالجة أخطاء الأوامر"""
    try:
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="❌ خطأ",
                description="الأمر غير موجود! استخدم `!help` لرؤية الأوامر",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ خطأ",
                description="الأمر يحتاج معاملات إضافية!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            logger.error(f"❌ خطأ: {error}")
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الأخطاء: {e}")

# ===== تشغيل البوت =====

async def main():
    """دالة التشغيل الرئيسية"""
    async with bot:
        if TOKEN:
            try:
                await bot.start(TOKEN)
            except Exception as e:
                logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        else:
            logger.error("❌ لم يتم العثور على TOKEN في config.json!")
            logger.info("🔧 الرجاء إضافة TOKEN الخاص بك في config.json")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ تم إيقاف البوت يدوياً")
    except Exception as e:
        logger.error(f"❌ خطأ فادح: {e}")
