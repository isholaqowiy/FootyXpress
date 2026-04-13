import os
import httpx
import hashlib

API_KEY = os.getenv("NEWS_API_KEY")

async def fetch_football_news():
    url = f"https://newsapi.org/v2/everything?q=football+soccer&language=en&sortBy=publishedAt&pageSize=5&apiKey={API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
            if data.get("status") != "ok":
                return []
            
            articles = []
            for art in data.get("articles", []):
                articles.append({
                    "title": art["title"],
                    "description": art["description"][:150] + "..." if art["description"] else "No summary available.",
                    "url": art["url"],
                    "hash": hashlib.md5(art["url"].encode()).hexdigest()
                })
            return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
