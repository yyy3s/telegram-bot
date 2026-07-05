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

    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False
        }
    )

    try:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0 Safari/537.36"
            ),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        res = scraper.get(
            "https://iraqprices.com",
            headers=headers,
            timeout=20
        )

        print("Status:", res.status_code)

        if res.status_code != 200:
            return None, None, None

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        text = soup.get_text(" ")

        # تحويل الأرقام العربية
        text = text.translate(
            str.maketrans(
                "٠١٢٣٤٥٦٧٨٩",
                "0123456789"
            )
        )

        text = (
            text
            .replace(",", "")
            .replace("،", "")
        )

        print("\n========== بداية النص ==========")
        print(text[:3000])

        # أخذ جميع أسعار 100$ موازي
        matches = re.findall(
            r'موازي.*?100\$.*?(\d{6})',
            text,
            re.DOTALL
        )

        print("\n========== الأسعار المكتشفة ==========")
        print(matches)

        if not matches:
            print("لم يتم العثور على سعر")
            return None, None, None

        # نأخذ آخر قيمة (الأحدث)
        price_100 = int(matches[-1])

        # تحويل إلى سعر الدولار الواحد
        price = price_100 // 100

        print("\n========== السعر النهائي ==========")
        print(f"100$ = {price_100}")
        print(f"1$ = {price}")

        return price, price, "IraqPrices"

    except Exception as e:
        print(f"خطأ: {e}")

    return None, None, None


# ================= إرسال الرسالة =================
def send_message(message):

    try:

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
        )

        print("\n========== نتيجة الإرسال ==========")
        print(response.status_code)
        print(response.text)

        return response.status_code == 200

    except Exception as e:
        print(f"خطأ إرسال: {e}")
        return False


# ================= التشغيل =================
if __name__ == "__main__":

    sell, buy, source = get_real_price()

    if sell:

        last_price = None

        if os.path.exists("last_price.txt"):

            with open("last_price.txt", "r") as f:

                try:
                    last_price = int(
                        f.read().strip()
                    )
                except:
                    pass

        print("\n========== مقارنة ==========")
        print("الحالي:", sell)
        print("المحفوظ:", last_price)

        if sell == last_price:

            print("السعر لم يتغير")

        else:

            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell:,} دينار ➜ {sell*100:,}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )

            success = send_message(message)

            if success:

                with open(
                    "last_price.txt",
                    "w"
                ) as f:

                    f.write(str(sell))

                print("تم حفظ السعر الجديد")

    else:

        print("لم يتم العثور على السعر")
