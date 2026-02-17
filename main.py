import telebot
from telebot import types

# --- إعدادات المطور ---
TOKEN = '8461120531:AAEfZ5NmBvmQuo5lS0xN2twxnJt29kFIExU'
CH_ID = '@PPQPPQT'  # قناتك للاشتراك الإجباري
ADMIN_ID = 8046597897 # آيدي حسابك الشخصي

bot = telebot.TeleBot(TOKEN)

# قواعد البيانات
locks = {}
custom_commands = {"طرد": "طرد"}

# --- فحص الاشتراك الإجباري ---
def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        status = bot.get_chat_member(CH_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- فحص الرتبة ---
def get_rank(chat_id, user_id):
    if user_id == ADMIN_ID: return "المطور الاساسي"
    st = bot.get_chat_member(chat_id, user_id).status
    return "المالك" if st == 'creator' else "المدير" if st == 'administrator' else "عضو"

# --- رسالة الاشتراك الإجباري ---
@bot.message_handler(func=lambda m: not check_sub(m.from_user.id))
def force_subscribe(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("اشترك هنا أولاً 📢", url=f"https://t.me/{CH_ID.replace('@','')}"))
    bot.reply_to(message, "⚠️ عذراً، يجب عليك الاشتراك في قناة المطور لاستخدام البوت.", reply_markup=markup)

# --- أمر الآيدي الاحترافي (نفس صورتك بالضبط) ---
@bot.message_handler(func=lambda m: m.text in ["ايدي", "ايديي", "id"])
def send_id_pro(message):
    user = message.from_user
    rank = get_rank(message.chat.id, user.id)
    # الحصول على عدد الرسائل (افتراضي للتبسيط)
    msg_count = "943" 
    
    caption = (
        f"☆-user : @{user.username if user.username else 'لا يوجد'}\n"
        f"☆-msg : {msg_count}\n"
        f"☆-sta : {rank}\n"
        f"☆-id : {user.id}"
    )
    
    # محاولة إرسال الصورة الشخصية إذا وجدت
    try:
        photos = bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            bot.send_photo(message.chat.id, photos.photos[0][-1].file_id, caption=caption)
        else:
            bot.reply_to(message, caption)
    except:
        bot.reply_to(message, caption)

# --- قائمة الأوامر الرئيسية (الصورة 1) ---
@bot.message_handler(func=lambda m: m.text == "الاوامر")
def main_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(str(i), callback_data=f"menu_{i}") for i in range(1, 5)]
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("الالعاب", callback_data="games"),
               types.InlineKeyboardButton("المطور", url=f"https://t.me/{CH_ID.replace('@','')}"))
    
    bot.reply_to(message, "قائمة الأوامر\n──────\n1. م 1: أوامر الحماية\n2. م 2: إعدادات المجموعة\n3. م 3: القفل والفتح\n4. م 4: أوامر أخرى", reply_markup=markup)

# --- نظام أضف امر (التخصيص) ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("أضف أمر"))
def add_cmd(message):
    if get_rank(message.chat.id, message.from_user.id) not in ["المطور الاساسي", "المالك"]: return
    try:
        parts = message.text.split()
        old, new = parts[2], parts[3]
        custom_commands[new] = old
        bot.reply_to(message, f"✅ تم تفعيل الأمر: ({new}) بدلاً من ({old})")
    except:
        bot.reply_to(message, "❌ مثال: أضف أمر طرد دي")

# --- تنفيذ الأوامر وحماية المجموعة ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video'])
def handle_all(message):
    chat_id = message.chat.id
    if message.text:
        # تنفيذ الأوامر المخصصة (مثل دي)
        actual = custom_commands.get(message.text)
        if actual == "طرد" and message.reply_to_message:
            if get_rank(chat_id, message.from_user.id) != "عضو":
                bot.kick_chat_member(chat_id, message.reply_to_message.from_user.id)
                bot.reply_to(message, "🚀 تم الطرد بنجاح.")

# تشغيل البوت
bot.polling()
