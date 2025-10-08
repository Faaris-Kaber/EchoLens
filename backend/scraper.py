import requests
from newspaper import Article
from bs4 import BeautifulSoup


def scrape_article(url: str) -> dict:
    """extract article text from url"""
    try:
        # use newspaper3k for news sites
        article = Article(url)
        article.download()
        article.parse()
        
        return {
            "success": True,
            "text": article.text,
            "title": article.title,
            "authors": article.authors,
            "publish_date": str(article.publish_date) if article.publish_date else None,
            "url": url
        }
    except Exception as e:
        # fallback to beautifulsoup
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # grab text from paragraphs
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
            
            return {
                "success": True,
                "text": text,
                "title": soup.find('title').get_text() if soup.find('title') else None,
                "url": url
            }
        except Exception as fallback_error:
            return {
                "success": False,
                "error": str(fallback_error),
                "url": url
            }
