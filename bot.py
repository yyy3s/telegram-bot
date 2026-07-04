import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

# ================= الإعدادات =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ================= دالة سحب الأسعار =================
def get_real_price():

    scraper = cloudscraper.create_scraper()

    try:
        res = scraper.get(
            "https://iraqprices.com",
            timeout=15
        )

        if res.status_code != 200:
            print(f"خطأ بالموقع: {res.status_code}")
            return None, None, None

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        english_digits = '0123456789'

        trans_table = str.maketrans(
            arabic_digits,
            english_digits
        )

        clean_text = (
            soup.get_text(separator=" ")
            .translate(trans_table)
            .replace("،", "")
            .replace(",", "")
            .replace(".", "")
        )

        if "الكفاح" not in clean_text:
            return None, None, None

        idx = clean_text.find("الكفاح")
        context = clean_text[idx:idx+150]

        prices = re.findall(
            r'15\d{2}',
            context
        )

        if len(prices) >= 2:

            prices = sorted(
                list(
                    set(
                        [int(x) for x in prices]
                    )
                )
            )

            sell = prices[-1]
            buy = prices[0]

            return sell, buy, "Iraq-Prices"

    except Exception as e:
        print(f"خطأ جلب السعر: {e}")

    return None, None, None


# ================= قراءة آخر رسالة =================
def get_last_channel_message():

    try:

        scraper = cloudscraper.create_scraper()

        channel = CHANNEL_ID.replace(
            "@",
            ""
        )

        res = scraper.get(
            f"https://t.me/s/{channel}",
            timeout=15
        )

        if res.status_code != 200:
            return ""

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        messages = soup.find_all(
            "div",
            class_="tgme_widget_message_text"
        )

        if messages:
            return messages[-1].text

    except Exception as e:
        print(f"خطأ قراءة الرسالة: {e}")

    return ""


# ================= إرسال الرسالة =================
def send_message(message):

    try:

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
        )

        print(response.status_code)
        print(response.text)

    except Exception as e:
        print(f"خطأ الإرسال: {e}")


# ================= التشغيل =================
if __name__ == "__main__":

    sell, buy, source = get_real_price()

    if sell and buy:

        sell_str = f"{sell:,}"

        print(f"تم الجلب من: {source}")

      last_message = get_last_channel_message()

# استخراج آخر سعر من آخر منشور
last_price = re.findall(r'15\d{2}', last_message)

if last_price:
    last_price = int(last_price[0])

    if last_price == sell:
        print("السعر لم يتغير، لن يتم الإرسال")
        exit()

else:

            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell_str} دينار ➜ {sell * 100:,}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )

            send_message(message)

            print(
                f"تم النشر بنجاح: {sell}"
            )

    else:

        print(
            "لم يتم العثور على السعر"
        )
