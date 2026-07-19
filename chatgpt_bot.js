const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { Configuration, OpenAIApi } = require('openai');
const fs = require('fs');

// تحميل الإعدادات
const config = JSON.parse(fs.readFileSync('config.json', 'utf-8'));
const TRUSTED_USER_ID = config.TRUSTED_USER_ID || ''; // معرف حمزة
const OPENAI_API_KEY = config.OPENAI_API_KEY || '';
const DISCORD_TOKEN = config.DISCORD_TOKEN || '';

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.DirectMessages
    ]
});

const configuration = new Configuration({
    apiKey: OPENAI_API_KEY
});
const openai = new OpenAIApi(configuration);

// قائمة الأسئلة الممنوعة
const FORBIDDEN_TOPICS = [
    'الأسلحة',
    'المخدرات',
    'الجرائم',
    'الاختراق',
    'الإرهاب',
    'التمييز',
    'العنف',
    'الانتحار',
    'الإساءة'
];

client.on('ready', () => {
    console.log(`✅ البوت شغّال كـ ${client.user.tag}`);
    console.log(`🇸🇦 متخصص في محادثات حمزة السعودي`);
    
    // تحديث حالة البوت
    client.user.setPresence({
        activities: [{ name: 'محادثات آمنة مع حمزة 🇸🇦', type: 'WATCHING' }],
        status: 'online'
    });
});

client.on('messageCreate', async message => {
    // تجاهل رسائل البوت
    if (message.author.bot) return;
    
    // التحقق من أن المرسل هو حمزة فقط
    if (message.author.id !== TRUSTED_USER_ID) {
        return;
    }
    
    // التحقق من الأمر
    if (!message.content.startsWith('!ask')) return;

    const userMessage = message.content.slice(5).trim();
    if (!userMessage) {
        const embed = new EmbedBuilder()
            .setColor('#FF0000')
            .setTitle('❌ خطأ')
            .setDescription('اكتب سؤالك بعد الأمر !ask\nمثال: `!ask كيف أطبخ الرز؟`');
        return message.reply({ embeds: [embed] });
    }

    // التحقق من الأسئلة الممنوعة
    const isBlacklisted = FORBIDDEN_TOPICS.some(topic => 
        userMessage.toLowerCase().includes(topic)
    );

    if (isBlacklisted) {
        const embed = new EmbedBuilder()
            .setColor('#FF0000')
            .setTitle('🚫 موضوع ممنوع')
            .setDescription('عذراً، لا يمكن الإجابة على هذا السؤال لأسباب أمنية.\nيرجى اختيار سؤال آخر آمن.');
        return message.reply({ embeds: [embed] });
    }

    // عرض رسالة التحميل
    const loadingEmbed = new EmbedBuilder()
        .setColor('#FFA500')
        .setTitle('⏳ جاري معالجة سؤالك...')
        .setDescription('الرجاء الانتظار قليلاً 🇸🇦');
    const loadingMsg = await message.reply({ embeds: [loadingEmbed] });

    try {
        const response = await openai.createChatCompletion({
            model: 'gpt-3.5-turbo',
            messages: [
                {
                    role: 'system',
                    content: 'أنت مساعد ذكي ودود بـ اللهجة السعودية. تساعد حمزة في الإجابة على أسئلته بشكل آمن ومفيد. الرد دائماً باللهجة السعودية بطريقة ودية وودية. لا تجاوب على أسئلة تتعلق بـ الأسلحة أو المخدرات أو الجرائم أو أي محتوى خطير.'
                },
                {
                    role: 'user',
                    content: userMessage
                }
            ],
            max_tokens: 1000,
            temperature: 0.7
        });

        const reply = response.data.choices[0].message.content;

        // إنشاء embed للإجابة
        const replyEmbed = new EmbedBuilder()
            .setColor('#00FF00')
            .setTitle('✅ الإجابة')
            .setDescription(reply)
            .setFooter({ text: '🇸🇦 محادثة آمنة مع حمزة' });

        // حذف رسالة التحميل والرد بالإجابة
        await loadingMsg.delete();
        await message.reply({ embeds: [replyEmbed] });

    } catch (error) {
        console.error('❌ خطأ:', error);
        
        const errorEmbed = new EmbedBuilder()
            .setColor('#FF0000')
            .setTitle('❌ حدث خطأ')
            .setDescription('عذراً، حدث خطأ. تحقق من:\n• المفتاح صحيح\n• الاتصال بالإنترنت\n• حد أقصى للطلبات');
        
        await loadingMsg.delete();
        await message.reply({ embeds: [errorEmbed] });
    }
});

// رسالة خطأ عند محاولة شخص آخر
client.on('messageCreate', async message => {
    if (message.author.bot) return;
    
    if (!message.content.startsWith('!ask')) return;
    
    if (message.author.id !== TRUSTED_USER_ID) {
        const embed = new EmbedBuilder()
            .setColor('#FF0000')
            .setTitle('🚫 ممنوع')
            .setDescription('عذراً، هذا البوت متخصص في محادثات حمزة السعودي فقط! 🇸🇦');
        return message.reply({ embeds: [embed] });
    }
});

client.login(DISCORD_TOKEN);
