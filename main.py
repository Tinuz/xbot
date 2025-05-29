import random
import tweepy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import datetime

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

# === 2. Google Sheets setup ===
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)  # ← service account bestand
client = gspread.authorize(creds)

spreadsheet = client.open("Foorfur X Campaign")  # ← pas aan
sheet = spreadsheet.sheet1

# Haal alle waarden op
rows = sheet.get_all_records()  # lijst van dicts
available_posts = [(i + 2, row['Post']) for i, row in enumerate(rows) if not row['Placed']]  # +2: skip header + 1-based index

if not available_posts:
    print("Geen ongebruikte berichten meer.")
    exit()

# Kies willekeurige ongebruikte post
row_number, message = random.choice(available_posts)

# === 3. Twitter (X) API setup ===
# Twitter API v2 client (werkt met Free tier)
client = tweepy.Client(
    consumer_key="jUEuC0G5RK2ve1wcpThATfReK",
    consumer_secret="2IMvvIIizvTptGP3hG57CDrF0AlL3b3OsLEclFRcwxhlfdsbMi",
    access_token="1923829352946376704-A7tdOzl5LV1C6FlOE6m9imNMmdrCa6",
    access_token_secret="fw06vF6rkya333L6ZcGEN2I11xOxEpmD4pbWBVpsVmNdR"
)

# Bericht posten via v2
try:
    response = client.create_tweet(text=message)
    print("✅ Tweet geplaatst met ID:", response.data["id"])
    sheet.update_cell(row_number, 2, 'TRUE')
    print("📌 Post gemarkeerd als geplaatst.")
except Exception as e:
    print("❌ Fout bij tweeten:", e)
