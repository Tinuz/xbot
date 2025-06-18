import tweepy
import openai
import os

from dotenv import load_dotenv
load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def generate_tweet():
    prompt = "Write a random short and absurd tweet, in the voice of Foofur."
    # API-call naar OpenAI
    try:
        response = openai.responses.create(
            model="gpt-4o",
            instructions="You are Foofur, a confused blue dog who accidentally created a memecoin by shoving his chew toy into a toaster. You tweet in third person with a dry, ironic tone. Your posts parody Web3 culture, always sound confident and clueless at the same time, and often reference absurd mechanics like token burns, fake utility, or shill quests. Keep it short, weird, and satirical. Never explain the joke. No hashtags unless part of the joke. Use $FOOF when relevant. Tone: self-aware, deadpan, chaotic, and a little broken.",
            input=prompt,
            max_output_tokens=140,
            temperature=0.7
        )

        # Print resultaat
        tweet = tweet = response.output[0].content[0].text
        return tweet

    except Exception as e:
        print("Error generating tweet:", e)
        return None

# === 4. X (Twitter) API setup ===
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET)
try:
    # Tweet plaatsen
    message = generate_tweet()

    if message:
        response = client.create_tweet(text=message)
        tweet_id = response.data["id"]

        # Gebruikersnaam ophalen om URL te bouwen
        user_response = client.get_me()
        username = user_response.data.username
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

        print("✅ Tweet geplaatst met ID:", tweet_id)
        print("🔗 URL:", tweet_url)
    else:
        print("❌ Geen tweet gegenereerd, dus niet gepost.")

except Exception as e:
    print("❌ Fout bij tweeten:", e)
except Exception as e:
    print("❌ Fout bij tweeten:", e)
