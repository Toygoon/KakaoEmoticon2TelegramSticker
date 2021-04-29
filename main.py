from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater
import telegram

apiKeyFile = open("/home/server/KakaoEmoticon2TelegramSticker_KEY", 'r')
TOKEN = apiKeyFile.read().rstrip('\n')
apiKeyFile.close()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def createEmoticon(update, context):
    emoticonURL = context.args[0]
    soupHeader = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    
    pageResource = requests.get(emoticonURL, headers=soupHeader)
    soup = BeautifulSoup(pageResource.text, features="html.parser")

    divContent = soup.find("div", id="kakaoContent")
    divInfo = divContent.find("div", class_="area_product")
    divTitle = divInfo.find("div", class_="info_product")
    strTitle = divTitle.find_all("span", class_="tit_inner")[0]

    context.bot.send_message(chat_id=update.effective_chat.id, text=strTitle)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot Started!")

create_handler = CommandHandler("create", createEmoticon)
start_handler = CommandHandler("start", start)

dispatcher.add_handler(create_handler)
dispatcher.add_handler(start_handler)

updater.start_polling()