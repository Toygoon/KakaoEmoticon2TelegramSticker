from telegram.ext import CommandHandler, Updater

from PIL import Image

from selenium import webdriver

from bs4 import BeautifulSoup
import urllib.request

import datetime
import os
import time
import keys

TOKEN = keys.TOKEN

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def createEmoticon(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="카카오 이모티콘 서비스에 접속하는 중입니다.")

    emoticonURL = context.args[0]

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36")
    driver = webdriver.Chrome(
        executable_path="chromedriver.exe", options=options)

    driver.get(emoticonURL)

    while (True):
        if scrollDownAllTheWay(driver):
            break

    context.bot.send_message(
        chat_id=update.effective_chat.id, text="이모티콘 정보를 불러오는 중입니다.")

    pageResource = driver.page_source
    soup = BeautifulSoup(pageResource, features="html.parser")

    divRoot = soup.find("div", id="root")
    divWrap = divRoot.find("div", id="kakaoWrap")
    divContent = divWrap.find("div", id="kakaoContent")
    divInfo = divContent.find("div", class_="area_product")
    divTitle = divInfo.find("div", class_="info_product")
    strTitle = divTitle.find("h3", class_="tit_product").text
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="%s 이모티콘을 다운로드 합니다." % (strTitle))

    divEmoticons = divContent.find("div", class_="area_emoticon")
    listEmoticons = divEmoticons.find("ul", class_="list_emoticon")
    itemEmoticons = listEmoticons.find_all("li")

    count = 0
    stickerName = ""

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="총 %d개의 이모티콘을 텔레그램 서버로 업로드합니다." % (len(itemEmoticons)))

    for srcEmoticon in itemEmoticons:
        urlEmoticon = srcEmoticon.find("img")["src"]
        urllib.request.urlretrieve(
            urlEmoticon, "./emoticonTemp/%d.png" % (count))

        img = Image.open("./emoticonTemp/%d.png" % (count))
        imgResize = img.resize((512, 512))
        imgResize.save("./emoticonTemp/%d.png" % (count))

        if count == 0:
            curTime = str(datetime.datetime.now().replace(
                tzinfo=datetime.timezone.utc).timestamp()).replace(".", "")
            stickerName = "t%s_by_KakaoEmoticon2Telegram_bot" % (curTime)
            context.bot.create_new_sticker_set(user_id=318996831,
                                               name=stickerName,
                                               title=strTitle,
                                               emojis="😀",
                                               contains_masks=False,
                                               png_sticker=open("./emoticonTemp/0.png", "rb"))
        else:
            context.bot.add_sticker_to_set(user_id=318996831,
                                           name=stickerName,
                                           emojis="😀",
                                           png_sticker=open("./emoticonTemp/%d.png" % (count), "rb"))

        os.remove("./emoticonTemp/%d.png" % (count))

        count += 1

    driver.close()

    context.bot.send_message(
        chat_id=update.effective_chat.id, text="%s 스티커 생성이 완료되었습니다!" % (strTitle))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="https://t.me/addstickers/%s" % (stickerName))


def helpMenu(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Help Menu")


def startBot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Bot Started!")


def stopBot(update, context):
    updater.stop()
    updater.is_idle = False


def scrollDown(driver, value):
    driver.execute_script("window.scrollBy(0,"+str(value)+")")


def scrollDownAllTheWay(driver):
    old_page = driver.page_source
    while True:
        for i in range(2):
            scrollDown(driver, 500)
            time.sleep(2)
        new_page = driver.page_source
        if new_page != old_page:
            old_page = new_page
        else:
            break
    return True


if __name__ == "__main__":
    start_handler = CommandHandler("start", startBot)
    create_handler = CommandHandler("create", createEmoticon)
    help_handler = CommandHandler("help", helpMenu)

    dispatcher.add_handler(create_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(start_handler)

    updater.start_polling()
