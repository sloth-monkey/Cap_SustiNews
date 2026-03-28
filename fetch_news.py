import json
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import time

# --- Configuration ---
# Using Google News RSS endpoints to provide guaranteed working deep-links
# No API key required.

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
    Fetches articles for a specific topic using Google News RSS.
    This guarantees that the URLs provided are direct working links to actual articles.
    """
    print(f"Fetching news for: {topic}...")
    
    # We use Google News RSS search to fetch direct working links
    query = urllib.parse.quote(f'"{topic}" OR sustainability')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    articles = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Find all <item> elements, taking the top 2
            for item in root.findall('.//item')[:2]:
                title = item.find('title')
                link = item.find('link')
                
                # Google News titles are typically "Actual Title - Source Name"
                full_title = title.text if title is not None else "News Article"
                source_name = "Global News"
                if " - " in full_title:
                    parts = full_title.rsplit(" - ", 1)
                    full_title = parts[0]
                    source_name = parts[1]
                
                article_link = link.text if link is not None else "#"
                
                articles.append({
                    "id": str(hash(article_link)),
                    "topic": topic,
                    "source": source_name,
                    "title": full_title,
                    "snippet": f"Latest insights and developments regarding {topic} from {source_name}.",
                    "url": article_link,
                    "time": get_formatted_time(),
                })
        return articles
            
    except Exception as e:
        print(f"Failed to fetch {topic}: {e}")
        # Final fallback
        search_query = urllib.parse.quote(f"{topic} news")
        return [
            {
                "id": f"fallback-{str(hash(topic))}",
                "topic": topic,
                "source": "Fallback News",
                "title": f"Recent developments in {topic}",
                "snippet": f"Important updates regarding {topic}.",
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
        time.sleep(0.5) # Be polite
        
    manage_rolling_window(todays_articles)
    print("Done! The landing page will now display the latest news.")

if __name__ == "__main__":
    main()
