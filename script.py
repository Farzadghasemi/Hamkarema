import json
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import re

# لیست منابع
SOURCES = [
    {
        "type": "rss",
        "name": "وزارت راه و شهرسازی",
        "url": "http://news.mrud.ir/rss"
    },
    {
        "type": "rss", # قطره RSS دارد، پس از نوع rss استفاده کنید
        "name": "قطره (ساختمان)",
        "url": "https://www.ghatreh.com/news/tag-48993-0-20.rss"
    },
    {
        "type": "html",
        "name": "نظام مهندسی کشور",
        "url": "https://irceo.ir/index.php/archive/news",
        "selector": "h3 a, h4 a, .news-title a" # سلکتورهای عمومی‌تر
    },
    {
        "type": "html",
        "name": "مقررات ملی ساختمان",
        "url": "https://inbr.ir/",
        "selector": "article h2 a, .post-title a"
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

# --- تابع جدید برای اصلاح لینک‌ها ---
def clean_link(link, base_url):
    if not link: return ""
    
    # حذف فاصله‌های اضافی
    link = link.strip()
    
    # رفع باگ قطره (لینک‌های دوپلی شده)
    # اگر لینک شامل دو بار http شد، آن را درست کن
    if "http" in link[4:]: 
        # پیدا کردن آخرین http
        match = re.search(r'(https?://.*)', link[4:])
        if match:
            link = match.group(1)

    # اگر لینک نسبی است (با / شروع شده)، کاملش کن
    if link.startswith('/'):
        # حذف اسلش آخر base_url اگر وجود دارد
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        return base_url + link
    
    # اگر لینک کامل نیست و اسلش هم ندارد (مثل page.html)
    if not link.startswith('http'):
        if base_url.endswith('/'):
            return base_url + link
        return base_url + '/' + link
        
    return link

def get_rss_news(source):
    news_items = []
    try:
        print(f"Fetching RSS: {source['name']}...")
        feed = feedparser.parse(source['url'])
        for entry in feed.entries[:4]:
            link = clean_link(entry.link, source['url']) # اصلاح لینک
            news_items.append({
                "title": entry.title,
                "link": link,
                "source": source['name']
            })
    except Exception as e:
        print(f"Error RSS {source['name']}: {e}")
    return news_items

def get_html_news(source):
    news_items = []
    try:
        print(f"Scraping HTML: {source['name']}...")
        # افزایش تایم‌اوت به ۳۰ ثانیه برای سایت‌های کند دولتی
        response = requests.get(source['url'], headers=HEADERS, timeout=30, verify=False) 
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.select(source['selector'])
            
            count = 0
            base_domain = "/".join(source['url'].split("/")[:3]) # استخراج دامنه اصلی (مثل https://inbr.ir)

            for link in links:
                if count >= 4: break
                
                title = link.get_text(strip=True)
                href = link.get('href')
                
                # تمیزکاری لینک با تابع جدید
                full_link = clean_link(href, base_domain)
                
                if title and len(title) > 10 and full_link:
                    news_items.append({
                        "title": title,
                        "link": full_link,
                        "source": source['name']
                    })
                    count += 1
    except Exception as e:
        print(f"Error HTML {source['name']}: {e}")
    return news_items

def get_prices():
    return [
        {"name": "میلگرد ۱۴ (ذوب)", "price": "۲۶,۲۰۰"},
        {"name": "تیرآهن ۱۶", "price": "۴,۸۰۰,۰۰۰"},
        {"name": "سیمان پاکتی", "price": "۷۹,۰۰۰"},
        {"name": "دلار آزاد", "price": "۶۰,۹۰۰"}
    ]

if __name__ == "__main__":
    # غیرفعال کردن اخطارهای امنیتی SSL (چون سایت‌های ایرانی گاهی مشکل SSL دارند)
    requests.packages.urllib3.disable_warnings()

    final_news = []
    for src in SOURCES:
        if src['type'] == 'rss':
            final_news.extend(get_rss_news(src))
        else:
            final_news.extend(get_html_news(src))
    
    data = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "market": get_prices(),
        "news": final_news,
        "regulations": {
            "9": "https://inbr.ir",
            "10": "https://inbr.ir"
        }
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Done!")
