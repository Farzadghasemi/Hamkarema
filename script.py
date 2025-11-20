import json
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

# لیست منابع خبری (ترکیبی از RSS و HTML)
SOURCES = [
    {
        "type": "rss",
        "name": "وزارت راه و شهرسازی",
        "url": "http://news.mrud.ir/rss"
    },
    {
        "type": "rss",
        "name": "قطره (ساختمان)",
        "url": "https://www.ghatreh.com/news/tag-48993-0-20.rss"
    },
    {
        "type": "html",
        "name": "شورای مرکزی نظام مهندسی",
        "url": "https://irceo.ir/index.php/archive/news",
        # این سلکتورها بر اساس ساختار معمول سایت‌ها حدس زده شده‌اند
        # در صورت تغییر قالب سایت، ممکن است نیاز به بازبینی باشد
        "selector": ".news-list h3 a, .archive-item h4 a, .content a.title" 
    },
    {
        "type": "html",
        "name": "مقررات ملی ساختمان",
        "url": "https://inbr.ir/",
        "selector": "article h2 a, .post-title a, .recent-news a"
    }
]

# تنظیمات درخواست (برای اینکه سایت‌ها ربات را مسدود نکنند)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_rss_news(source):
    news_items = []
    try:
        print(f"Fetching RSS: {source['name']}...")
        feed = feedparser.parse(source['url'])
        for entry in feed.entries[:4]: # فقط ۴ خبر اول
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "source": source['name']
            })
    except Exception as e:
        print(f"Error fetching RSS {source['name']}: {e}")
    return news_items

def get_html_news(source):
    news_items = []
    try:
        print(f"Scraping HTML: {source['name']}...")
        response = requests.get(source['url'], headers=HEADERS, timeout=15)
        response.encoding = 'utf-8' # جلوگیری از بهم ریختن فونت فارسی
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # تلاش برای پیدا کردن لینک‌ها با سلکتورهای مختلف
            # ما تمام سلکتورهای احتمالی را با کاما جدا کردیم
            links = soup.select(source['selector'])
            
            count = 0
            for link in links:
                if count >= 4: break # محدودیت ۴ خبر
                
                title = link.get_text(strip=True)
                href = link.get('href')
                
                # اگر لینک کامل نبود (نسبی بود)، کاملش کن
                if href and not href.startswith('http'):
                    # استخراج دامنه اصلی
                    base_url = "/".join(source['url'].split("/")[:3])
                    href = base_url + href
                
                if title and len(title) > 10: # حذف تیترهای خیلی کوتاه یا خالی
                    news_items.append({
                        "title": title,
                        "link": href,
                        "source": source['name']
                    })
                    count += 1
    except Exception as e:
        print(f"Error scraping HTML {source['name']}: {e}")
    return news_items

def get_prices():
    # قیمت‌ها فعلا استاتیک یا با منطق قبلی
    # برای توسعه بعدی می‌توانید برای این‌ها هم Scraper بنویسید
    return [
        {"name": "میلگرد ۱۴ (ذوب)", "price": "۲۶,۲۰۰"},
        {"name": "تیرآهن ۱۶", "price": "۴,۸۰۰,۰۰۰"},
        {"name": "سیمان پاکتی", "price": "۷۹,۰۰۰"},
        {"name": "دلار آزاد", "price": "۶۰,۹۰۰"}
    ]

if __name__ == "__main__":
    final_news = []
    
    # پردازش تمام منابع
    for src in SOURCES:
        if src['type'] == 'rss':
            final_news.extend(get_rss_news(src))
        else:
            final_news.extend(get_html_news(src))
    
    # ساختار نهایی فایل JSON
    data = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "market": get_prices(),
        "news": final_news, # لیست پر شده از خبرها
        "regulations": {
            "9": "https://inbr.ir", 
            "10": "https://inbr.ir"
        }
    }

    # ذخیره فایل
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Done! data.json updated.")
