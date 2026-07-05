import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

# ================= الإعدادات =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ================= جلب السعر =================
def get_real_price():

    scraper = cloudscraper.create_scraper()

    try:

        res = scraper.get(
            "https://iraqprices.com",
            headers={
                "User-Agent": "Mozilla/5.0"
            },
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
            print("لم يتم العثور على كلمة الكفاح")
            return None, None, None

        idx = clean_text.find("الكفاح")

        # وسعنا البحث
        context = clean_text[idx:idx+500]

        print("\n========== النص المستخرج ==========")
        print(context)

        prices = re.findall(
            r'15\d{2}',
            context
        )

        print("\n========== الأسعار المكتشفة ==========")
        print(prices)

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

            print(f"\nبيع: {sell}")
            print(f"شراء: {buy}")

            return sell, buy, "Iraq-Prices"

        print("ماكو أسعار كافية")

    except Exception as e:
        print(f"خطأ جلب السعر: {e}")

    return None, None, None


# ================= إرسال رسالة =================
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

        print("\n========== نتيجة الإرسال ==========")
        print(response.status_code)
        print(response.text)

    except Exception as e:
        print(f"خطأ الإرسال: {e}")


# ================= التشغيل =================
if __name__ == "__main__":

    sell, buy, source = get_real_price()

    if sell and buy:

        sell_str = f"{sell:,}"

        last_price = None

        # قراءة آخر سعر
        if os.path.exists("last_price.txt"):

            with open(
                "last_price.txt",
                "r"
            ) as f:

                try:
                    last_price = int(
                        f.read().strip()
                    )

                except:
                    pass

        print("\n========== مقارنة الأسعار ==========")
        print(f"السعر الحالي: {sell}")
        print(f"آخر سعر محفوظ: {last_price}")

        if last_price == sell:

            print("السعر لم يتغير، لن يتم الإرسال")

        else:

            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell_str} دينار ➜ {sell * 100:,}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )

            send_message(message)

            with open(
                "last_price.txt",
                "w"
            ) as f:

                f.write(
                    str(sell)
                )

            print(
                f"تم النشر: {sell}"
            )

    else:

        print(
            "لم يتم العثور على السعر"
        )
