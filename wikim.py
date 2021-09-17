import telebot
from telebot.types import Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import sqlite3 as sql
import wikipedia as w

dbfile = "data.db"

with sql.connect(dbfile) as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS user(
        id INTEGER,
        name TEXT,
        wlang TEXT)""")

    con.commit()

def insert(userid, u_name, wlang):
    con = sql.connect(dbfile)
    cur = con.cursor()
    cur.execute("SELECT * FROM user WHERE id = ?", (userid,))

    if cur.fetchone() is None:

        cur.execute("INSERT INTO user(id,name,wlang) VALUES(?,?,?)", (userid, u_name, wlang))
    con.commit()

def uplang(lang, chatid):
    con = sql.connect(dbfile)
    cur = con.cursor()
    cur.execute("SELECT wlang FROM user WHERE id = ?",(chatid,))
    l = cur.fetchall()
    for la in l:
        lan = la[0]
    
    cur.execute("UPDATE user SET wlang = ? WHERE wlang = ?", (lang, lan))
    con.commit()


#buttons

soz = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton('⚙️ Sozlamalar', callback_data='soz')
    ]]
)

til = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton('🇺🇿 UZ', callback_data='uz'),
        InlineKeyboardButton('🇷🇺 RU', callback_data='ru'),
        InlineKeyboardButton('🏴󠁧󠁢󠁥󠁮󠁧󠁿 EN', callback_data='en')
    ]]
)

token = "token"

bot = telebot.TeleBot(token, parse_mode="markdown")

@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    u_name = msg.from_user.first_name
    lang = 'uz'
    insert(chat_id,u_name,lang)
    bot.send_message(chat_id, f"👋 Salom [{msg.from_user.first_name}](tg://user?id={chat_id})\n\n*Men sizga Wikipedia dan maqolalarni qidirishga yordam beraman!*", reply_markup=soz)

@bot.callback_query_handler(func = lambda call: True)
def calls(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    data = call.data

    con = sql.connect(dbfile)
    cur = con.cursor()
    cur.execute("SELECT wlang FROM user WHERE id = ?", (chat_id,))
    a = cur.fetchall()
    for i in a:
        l = i[0]

    if data == 'soz':
        bot.edit_message_text("*Qidiruv tilini tanlang* 👇", chat_id, msg_id, reply_markup=til)
    if data == 'uz':
        tiluz = 'uz'
        uplang(tiluz, chat_id)
        bot.edit_message_text("🇺🇿 UZ o'rnatildi!", chat_id, msg_id)

    if data == 'ru':
        tilru = 'ru'
        uplang(tilru, chat_id)
        bot.edit_message_text("🇷🇺 RU o'rnatildi!", chat_id, msg_id)
    if data == 'en':
        tilen = 'en'
        uplang(tilen, chat_id)
        bot.edit_message_text("🏴󠁧󠁢󠁥󠁮󠁧󠁿 EN o'rnatildi!", chat_id, msg_id)
@bot.message_handler(content_types=['text'])
def wiki(msg):
    text = msg.text
    chat_id = msg.chat.id
    try:
        con = sql.connect(dbfile)
        cur = con.cursor()
        cur.execute("SELECT wlang FROM user WHERE id = ?", (chat_id,))
        a = cur.fetchall()
        for i in a:
            l = i[0]

        w.set_lang(l)
        r = w.summary(text)
        bot.send_message(msg.chat.id, r)
    except Exception as ex:
        bot.send_message(chat_id, f'Xatolik:\n{ex}')
    

bot.polling()
