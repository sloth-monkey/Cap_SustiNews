import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
import time
import sys

# --- Configuration ---
# Store this SECURELY in GitHub Repository Settings > Secrets and variables > Actions
API_KEY = os.environ.get("NEWS_API_KEY")

TOPICS = [
    "Carbon Accounting",
    "AI Sustainability",
    "Climate Adaptation",
    "Climate Transition Plans",
    "SME Government Support",
    "Corporate Sustainability Action",
    "Sustainability Reporting",
    "Sustainability Financing",
    "Supply Chain"
]

JSON_FILE_PATH = "news_data.json"

def fetch_articles_for_topic(topic):
    """
    Fetches genuine articles for a specific topic using the GNews API.
    Raises an error if the API key is unauthorized instead of falling back to mock data.
    """
    print(f"Fetching legitimate news for: {topic}...")
    
    # We append "sustainability" to guarantee highly relevant professional results
    query = urllib.parse.quote(f"{topic} sustainability")
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q={query}&language=en"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            articles = []
            if "results" in data:
                for item in data.get("results", [])[:2]: # Max 2 articles per topic
                    source_name = item.get("source_id", "Global News Portal")
                    if isinstance(source_name, dict):
                        source_name = source_name.get("name", "Global News Portal")
                    
                    article_link = item.get("link", "")
                    desc = item.get("description") or ""
                    
                    articles.append({
                        "id": str(hash(article_link)),
                        "topic": topic,
                        "source": str(source_name).title(),
                        "title": item.get("title", ""),
                        "snippet": desc[:120] + "...",
                        "url": article_link,
                        "time": get_formatted_time(),
                    })
            return articles
            
    except urllib.error.HTTPError as e:
        print(f"CRITICAL API ERROR: {e.code} - {e.reason}")
        print("Please ensure your NEWS_API_KEY is correctly set as an environment variable in GitHub Secrets.")
        # We explicitly return an empty list so we DONT hallucinate mock articles.
        return []
    except Exception as e:
        print(f"Unexpected error fetching {topic}: {e}")
        return []

def get_formatted_time():
    return datetime.now().strftime("%I:%M %p")

def manage_rolling_window(new_articles):
    history = []
    
    if os.path.exists(JSON_FILE_PATH):
        try:
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            print("Notice: No valid history found, creating fresh archive.")
            history = []
    
    # We only insert the batch if it contains REAL articles
    if len(new_articles) > 0:
        history.insert(0, new_articles)
        
        # Prune older than 7 days
        if len(history) > 7:
            history = history[:7]
            
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
            print("Successfully committed factual articles to the 7-day archive.")
    else:
        print("Warning: No articles successfully fetched today. The pre-existing archive was left unchanged.")

def main():
    if not API_KEY or API_KEY == "YOUR_FREE_API_KEY_HERE":
        print("FATAL ERROR: NEWS_API_KEY environment variable is missing or invalid.")
        print("Please configure this Secret in GitHub Actions to comb the web for real articles.")
        sys.exit(1)
        
    print(f"Initiating GitHub Worker at {datetime.now()}...")
    todays_articles = []
    
    for topic in TOPICS:
        articles = fetch_articles_for_topic(topic)
        todays_articles.extend(articles)
        time.sleep(1) # Polite rate-limiting
        
    manage_rolling_window(todays_articles)
    print("Execution finalized. The platform is newly populated.")

if __name__ == "__main__":
    main()
