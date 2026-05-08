import os
import html
import json
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, FloodWaitError, ApiIdInvalidError, SessionExpiredError
import asyncio

# گرفتن متغیرهای محیطی
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
telegram_session = os.getenv("TELEGRAM_SESSION")
channel_username = 'hattrick_channel'  # نام کانال شما

# بررسی وجود متغیرهای محیطی
if not api_id or not api_hash or not telegram_session:
    print("Error: Missing environment variables (TELEGRAM_API_ID, TELEGRAM_API_HASH, or TELEGRAM_SESSION)")
    exit(1)

# ایجاد کلاینت با StringSession
try:
    client = TelegramClient(StringSession(telegram_session), int(api_id), api_hash)
except Exception as e:
    print(f"Error initializing client: {e}")
    exit(1)

async def main():
    try:
        print("Attempting to connect to Telegram...")
        # اتصال به تلگرام
        await client.start()
        print("Connected to Telegram successfully")
        
        posts_html = '<div class="telegram-posts">\n'
        posts_json = []
        
        # خواندن پیام‌ها (فقط 5 پست اول)
        # استفاده از limit=5 به جای شمارنده دستی
        async for message in client.iter_messages(channel_username, limit=5):
            # بررسی اینکه پیام متن دارد
            if message.message and message.message.strip():
                # محدود کردن به 5 کلمه اول برای پیش‌نمایش
                words = message.message.strip().split()
                short_text = ' '.join(words[:5])
                if len(words) > 5:
                    short_text += '...'
                
                # ایمن‌سازی متن برای HTML
                text = html.escape(short_text)
                link = f'https://t.me/{channel_username}/{message.id}'
                date_str = message.date.strftime('%Y-%m-%d %H:%M')
                
                posts_html += f'<div class="telegram-post"><a href="{link}" target="_blank" class="post-link">{text}</a><br><small>{date_str}</small></div>\n'
                posts_json.append({
                    "text": message.message.strip(),
                    "date": int(message.date.timestamp()),
                    "link": link
                })
            else:
                print(f"Skipping message ID {message.id} (no text)")

        if not posts_json:
            print("No posts with text found in the last 5 messages.")
            posts_html += '<div class="telegram-post">پستی با متن یافت نشد.</div>\n'

        posts_html += '</div>'

        # ذخیره فایل‌ها (حتی اگر خطایی رخ داده باشد، این فایل‌ها را می‌سازیم تا گیت‌هاب خطا ندهد)
        with open('telegram-posts.html', 'w', encoding='utf-8') as f:
            f.write(posts_html)
        print("telegram-posts.html saved")

        with open('posts_formatted.json', 'w', encoding='utf-8') as f:
            json.dump(posts_json, f, ensure_ascii=False, indent=2)
        print("posts_formatted.json saved")

    except SessionPasswordNeededError:
        print("Error: Session expired or password needed. Please update your TELEGRAM_SESSION secret.")
        # ایجاد فایل‌های خالی یا قدیمی برای جلوگیری از خطای گیت
        with open('telegram-posts.html', 'w', encoding='utf-8') as f:
            f.write('<div class="telegram-posts">Error: Connection failed.</div>')
        with open('posts_formatted.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    except FloodWaitError as e:
        print(f"Error: Flood wait. Please wait {e.seconds} seconds.")
        # ایجاد فایل‌های خالی
        with open('telegram-posts.html', 'w', encoding='utf-8') as f:
            f.write('<div class="telegram-posts">Error: Flood wait.</div>')
        with open('posts_formatted.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    except ApiIdInvalidError:
        print("Error: Invalid API ID or Hash. Please check your secrets.")
        with open('telegram-posts.html', 'w', encoding='utf-8') as f:
            f.write('<div class="telegram-posts">Error: Invalid API ID.</div>')
        with open('posts_formatted.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        # ایجاد فایل‌های خالی برای جلوگیری از خطای گیت
        with open('telegram-posts.html', 'w', encoding='utf-8') as f:
            f.write('<div class="telegram-posts">Error: Unknown error.</div>')
        with open('posts_formatted.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    finally:
        try:
            await client.disconnect()
            print("Disconnected from Telegram")
        except:
            pass

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Main execution failed: {str(e)}")
        exit(1)
