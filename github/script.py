import json
import requests
import feedparser # برای خواندن RSS اخبار
from bs4 import BeautifulSoup # برای قیمت‌ها (Web Scraping)
from datetime import datetime

# 1. تنظیمات منابع خبری (RSS)
NEWS_SOURCES = [
    {"source": "ایسنا", "url": "https://www.isna.ir/rss"},
    {"source": "مهر", "url": "https://www.mehrnews.com/rss"},
    # لینک RSS نظام مهندسی یا سایت‌های دیگر را اینجا اضافه کنید
]

# 2. تابع دریافت اخبار
def get_news():
    news_list = []
    for src in NEWS_SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            # گرفتن 3 خبر اول هر منبع
            for entry in feed.entries[:3]:
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": src["source"]
                })
        except Exception as e:
            print(f"Error fetching {src['source']}: {e}")
    return news_list

# 3. تابع دریافت قیمت‌ها (مثال Scraping)
# نکته: سایت‌های قیمت طلا/ارز معمولا ساختارشان عوض می‌شود. این یک مثال است.
# پیشنهاد: برای قیمت، از API های رایگان مثل 'tgju' یا similar استفاده کنید.
def get_prices():
    prices = [
        {"name": "میلگرد ۱۴ (اصفهان)", "price": "۲۶,۵۰۰"}, # مثال استاتیک
        {"name": "سیمان تیپ ۲", "price": "۷۵,۰۰۰"},
    ]
    
    # تلاش برای گرفتن قیمت دلار (نمونه آموزشی)
    try:
        # اینجا را باید بر اساس یک سایت واقعی مثل tgju.org تنظیم کنید
        # r = requests.get('URL_SITE', headers={'User-Agent': 'Mozilla/5.0'})
        # soup = BeautifulSoup(r.text, 'html.parser')
        # dollar = soup.find('span', class_='price-tag').text
        prices.append({"name": "دلار آمریکا", "price": "۶۰,۵۰۰ (مثال)"})
    except:
        pass
        
    return prices

# 4. اجرای اصلی
if __name__ == "__main__":
    data = {
        "last_update": str(datetime.now()),
        "market": get_prices(),
        "news": get_news(),
        "regulations": { # لینک‌های ثابت
            "9": "LINK_PDF_9",
            "10": "LINK_PDF_10"
        }
    }

    # ذخیره در فایل
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Data updated successfully!")