import requests
from decouple import config


# Send Message
def send_message(message):
    bot_token1 = config("TELEGRAM_TOKEN1")
    chat_id1 = config("TELEGRAM_CHAT_ID1")
    url1 = f"https://api.telegram.org/bot{bot_token1}/sendMessage?chat_id={chat_id1}&text={message}"
    res1 = requests.get(url1)

    bot_token2 = config("TELEGRAM_TOKEN2")
    chat_id2 = config("TELEGRAM_CHAT_ID2")
    url2 = f"https://api.telegram.org/bot{bot_token2}/sendMessage?chat_id={chat_id2}&text={message}"
    res2 = requests.get(url2)

    bot_token3 = config("TELEGRAM_TOKEN3")
    chat_id3 = config("TELEGRAM_CHAT_ID3")
    url3 = f"https://api.telegram.org/bot{bot_token3}/sendMessage?chat_id={chat_id3}&text={message}"
    res3 = requests.get(url3)

    bot_token4 = config("TELEGRAM_TOKEN4")
    chat_id4 = config("TELEGRAM_CHAT_ID4")
    url4 = f"https://api.telegram.org/bot{bot_token4}/sendMessage?chat_id={chat_id4}&text={message}"
    res4 = requests.get(url4)