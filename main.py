import random
import tweepy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import datetime
import os
from dotenv import load_dotenv

# === .env laden ===
load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# === 1. Bereken geplande posttijd met random offset ===
offset_minutes = random.randint(-10, 10)
now = datetime.datetime.now()
next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
scheduled_time = next_hour + datetime.timedelta(minutes=offset_minutes)

# === 2. Toon geplande tijd en start countdown ===
wait_seconds = int((scheduled_time - now).total_seconds())

if wait_seconds > 0:
    print(f"⏰ Bericht wordt geplaatst om: {scheduled_time.strftime('%H:%M:%S')}")
    print(f"⌛ Start aftellen ({wait_seconds} seconden):\n")

    try:
        for remaining in range(wait_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_display = f"{mins:02d}:{secs:02d}"
            print(f"\r⏳ Tijd tot post: {time_display}", end="")
            time.sleep(1)
        print("\n🟢 Tijd om te posten!\n")
    except KeyboardInterrupt:
        print("\n⛔ Aftellen onderbroken door gebruiker.")
        exit()

else:
    print("⏩ Tijdstip ligt al in het verleden, ga meteen door.\n")

# === 3. Google Sheets setup ===
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gs_client = gspread.authorize(creds)

spreadsheet = gs_client.open("Foorfur X Campaign")
sheet = spreadsheet.sheet1

rows = sheet.get_all_records()
available_posts = [(i + 2, row['Post']) for i, row in enumerate(rows) if not row['Placed']]

if not available_posts:
    print("⚠️ Geen ongebruikte berichten meer.")
    exit()

row_number, message = random.choice(available_posts)

# === 4. X (Twitter) API setup ===
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

try:
    response = client.create_tweet(text=message)
    print("✅ Tweet geplaatst met ID:", response.data["id"])
    sheet.update_cell(row_number, 2, 'TRUE')
    print("📌 Post gemarkeerd als geplaatst.")
except Exception as e:
    print("❌ Fout bij tweeten:", e)
