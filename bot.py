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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://google.com/"
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

        # تحويل الأرقام العربية لإنكليزية
        arabic_digits = "٠١٢٣٤٥٦٧٨٩"
        english_digits = "0123456789"

        text = text.translate(
            str.maketrans(
                arabic_digits,
                english_digits
            )
        )

        text = (
            text
            .replace("،", "")
            .replace(",", "")
            .replace(".", "")
        )

        idx = text.find("الكفاح")

        if idx == -1:
            print("لم يتم العثور على كلمة الكفاح")
            return None, None, None

        context = text[idx:idx+500]

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

            buy = prices[0]
            sell = prices[-1]

            print(f"\nشراء: {buy}")
            print(f"بيع: {sell}")

            return sell, buy, "IraqPrices"

        print("لم يتم العثور على أسعار")

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

    if sell and buy:

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

            sell_str = f"{sell:,}"

            message = (
                f"💵 *تحديث سعر الدولار الآن*\n\n"
                f"📍¦ *بورصة الكفاح*\n"
                f"🔻¦ {sell_str} دينار ➜ {sell * 100:,}\n"
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
