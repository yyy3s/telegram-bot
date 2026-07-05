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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ar-IQ,ar;q=0.9,en-US;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        res = scraper.get(
            "https://iraqprices.com",
            headers=headers,
            timeout=20
        )

        print(f"Status Code: {res.status_code}")

        if res.status_code != 200:
            print("فشل الوصول للموقع")
            return None, None, None

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        text = soup.get_text(" ")

        # تحويل الأرقام العربية إلى إنكليزية
        text = text.translate(
            str.maketrans(
                "٠١٢٣٤٥٦٧٨٩",
                "0123456789"
            )
        )

        text = (
            text
            .replace("،", "")
            .replace(",", "")
        )

        print("\n========== النص المستخرج ==========")
        print(text[:1500])

        # استخراج سعر 100$ موازي الكفاح
        match = re.search(
            r'موازي\s*\(الكفاح\)\s*(\d{6})',
            text
        )

        if not match:
            print("لم يتم العثور على سعر الكفاح")
            return None, None, None

        price_100 = int(
            match.group(1)
        )

        # تحويله لسعر الدولار الواحد
        price = price_100 // 100

        print("\n========== السعر ==========")
        print(f"100$ = {price_100}")
        print(f"1$ = {price}")

        return price, price, "IraqPrices"

    except Exception as e:
        print(f"خطأ جلب السعر: {e}")

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
        print(f"خطأ الإرسال: {e}")
        return False


# ================= التشغيل =================
if __name__ == "__main__":

    sell, buy, source = get_real_price()

    if sell:

        last_price = None

        # قراءة آخر سعر محفوظ
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

        # إذا لم يتغير السعر
        if last_price == sell:

            print("السعر لم يتغير، لن يتم الإرسال")

        else:

            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell:,} دينار ➜ {sell * 100:,}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"https://t.me/DollarNowIQ"
            )

            success = send_message(message)

            if success:

                with open(
                    "last_price.txt",
                    "w"
                ) as f:

                    f.write(
                        str(sell)
                    )

                print(f"تم النشر: {sell}")

    else:

        print("لم يتم العثور على السعر")
