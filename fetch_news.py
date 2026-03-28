import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
import time

# --- Configuration ---
# You will get this key for free from a service like NewsData.io or GNews.io
# Make sure to securely store it in your GitHub Repository settings under Settings > Secrets and variables > Actions
API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_FREE_API_KEY_HERE")

TOPICS = [
    "Carbon Accounting",
    "AI Sustainability",
    "Climate Adaptation",
    "Climate Transition Plans",
    "SME Government Support",
    "Corporate Sustainability Action",
    "Sustainability Reporting",
    "Sustainability Financing"
]

JSON_FILE_PATH = "news_data.json"

def fetch_articles_for_topic(topic):
    """
    Fetches articles for a specific topic using a free News API.
    Since premium sources like FT and Bloomberg often block free APIs, 
    we perform a broad query for the topic but prioritize business/financial news.
    """
    print(f"Fetching news for: {topic}...")
    
    # Example using GNews Free API - Returns structured JSON
    # 'q' is our search query, 'max' limits the results per topic to save space
    # In production, replace the URL with the exact endpoint of your chosen provider
    query = urllib.parse.quote(topic)
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max=3&apikey={API_KEY}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            articles = []
            if "articles" in data:
                for item in data["articles"]:
                    source_name = item.get("source", {}).get("name", "Financial/Global News")
                    
                    articles.append({
                        "id": str(hash(item.get("url", ""))),
                        "topic": topic,
                        "source": source_name,
                        "title": item.get("title", ""),
                        "snippet": item.get("description", "")[:120] + "...", # truncate
                        "url": item.get("url", "#"),
                        "time": get_formatted_time(),
                    })
            return articles
            
    except Exception as e:
        print(f"Failed to fetch {topic}: {e}")
        # Return fallback mock structured data if the API fails or no key is provided
        search_query = urllib.parse.quote(f"{topic} news")
        return [
            {
                "id": f"fallback-{str(hash(topic))}",
                "topic": topic,
                "source": "Financial Times (Simulated)",
                "title": f"New Policy Mandates for {topic}",
                "snippet": "Regulators are accelerating deadlines for corporate compliance in this sector.",
                "url": f"https://news.google.com/search?q={search_query}",
                "time": get_formatted_time(),
            }
        ]

def get_formatted_time():
    """Returns the current time formatted for the UI (e.g., 8:30 AM)"""
    return datetime.now().strftime("%I:%M %p")

def manage_rolling_window(new_articles):
    """
    Loads the existing 7-day archive, pushes the new day's articles to index 0,
    and removes the oldest day to maintain a max 7-day history.
    """
    history = []
    
    # Load existing history if it exists
    if os.path.exists(JSON_FILE_PATH):
        try:
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception as e:
            print("Error reading existing history, starting fresh.")
            history = []
    
    # Insert today's newly fetched batch at the start (index 0)
    history.insert(0, new_articles)
    
    # Ensure we only keep 7 days of data
    if len(history) > 7:
        history = history[:7]
        
    # Save the updated rolling window back to JSON
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)
        print("Successfully updated the 7-day archive.")

def main():
    print(f"Starting Daily News Fetcher at {datetime.now()}...")
    
    todays_articles = []
    
    for topic in TOPICS:
        articles = fetch_articles_for_topic(topic)
        todays_articles.extend(articles)
        time.sleep(1) # Be polite to the free API rate limits!
        
    manage_rolling_window(todays_articles)
    print("Done! The landing page will now display the latest news.")

if __name__ == "__main__":
    main()
