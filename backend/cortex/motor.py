try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

try:
    from googlesearch import search as google_search_api
except ImportError:
    google_search_api = None

import requests
from bs4 import BeautifulSoup
import sys
from io import StringIO
import contextlib
import re

# User agent to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

def search_with_google_official(query: str, max_results: int = 5) -> list:
    """
    Primary Search: Use 'googlesearch-python' to get real Google results.
    Filters out Wikipedia if requested.
    """
    if not google_search_api:
        return []

    print(f"DEBUG: Using Google Search for: {query}")
    results = []
    
    try:
        # Fetch more results to allow for filtering
        # 'advanced=True' returns Result objects with title/description/url
        search_gen = google_search_api(query, num_results=max_results + 5, advanced=True)
        
        for result in search_gen:
            if len(results) >= max_results:
                break
            
            # Helper to safely get attribute or dict item
            def get_val(obj, attr):
                return getattr(obj, attr, obj.get(attr) if isinstance(obj, dict) else None)

            url = get_val(result, 'url') or get_val(result, 'link')
            
            # Filter: Exclude Wikipedia
            if url and "wikipedia.org" in url.lower():
                print(f"DEBUG: Filtered out Wikipedia: {url}")
                continue
                
            results.append({
                'title': get_val(result, 'title'),
                'body': get_val(result, 'description') or get_val(result, 'snippet'),
                'href': url
            })
            
        print(f"DEBUG: Google Search yielded {len(results)} high-quality results.")
        
    except Exception as e:
        print(f"DEBUG: Google Search API failed: {e}")
    
    return results

def search_with_ddgs(query: str, max_results: int = 5) -> list:
    """Try DuckDuckGo search with multiple backends."""
    results = []
    
    # Try different backends in order
    backends = [None, "html", "lite"]
    
    for backend in backends:
        try:
            if backend:
                results = list(DDGS().text(query, max_results=max_results, backend=backend))
            else:
                results = list(DDGS().text(query, max_results=max_results))
            
            if results:
                print(f"DEBUG: Got {len(results)} results from DDGS (backend: {backend or 'default'})")
                return results
        except Exception as e:
            print(f"DEBUG: DDGS {backend or 'default'} failed: {str(e)[:100]}")
            continue
    
    return results

def search_with_requests(query: str, max_results: int = 5) -> list:
    """Fallback search using direct HTTP requests to DuckDuckGo HTML."""
    results = []
    
    try:
        # Use DuckDuckGo HTML version
        import urllib.parse
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find result divs
        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs[:max_results]:
            try:
                title_tag = div.find('a', class_='result__a')
                snippet_tag = div.find('a', class_='result__snippet')
                
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    href = title_tag.get('href', '')
                    body = snippet_tag.get_text(strip=True) if snippet_tag else ''
                    
                    if title and href:
                        results.append({
                            'title': title,
                            'body': body,
                            'href': href
                        })
            except Exception as e:
                print(f"Error parsing search result: {e}")
                continue
        
        print(f"DEBUG: Got {len(results)} results from direct HTTP request")
        
    except Exception as e:
        print(f"DEBUG: Direct HTTP search failed: {str(e)[:100]}")
    
    return results

def web_search(query: str) -> str:
    """Search the web for real-time information using Google (Primary) or others."""
    query = query.strip()
    
    try:
        print(f"DEBUG: Web search for: {query.encode('ascii', 'ignore').decode()}")
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        print(f"Unicode error in search query: {e}")
    
    results = []
    
    # Method 1: Google Search (Official) - User Request
    results = search_with_google_official(query)
    
    # Method 2: DuckDuckGo (Fallback)
    if not results and DDGS:
        print("DEBUG: Google failed. Falling back to DuckDuckGo...")
        results = search_with_ddgs(query)
    
    # Method 3: Direct HTTP to DuckDuckGo HTML (Last Resort)
    if not results:
        print("DEBUG: DDG failed. Trying direct HTTP request...")
        results = search_with_requests(query)
    
    
    if not results:
        return "No results found. The search services may be temporarily unavailable."
    
    # Format results
    formatted = []
    for r in results:
        title = r.get('title', 'No title')
        body = r.get('body', '')
        href = r.get('href', '')
        # Double check filtering just in case fallbacks returned wiki
        if "wikipedia.org" in href.lower():
            continue
            
        formatted.append(f"- {title}: {body} ({href})")
    
    return "\n".join(formatted)

def run_python(code: str) -> str:
    """Execute Python code in a sandboxed environment."""
    from execution_service import execution_service
    
    # Sanitize logs: Truncate code in logs to avoid leaking sensitive data or large payloads
    preview = code[:100] + "..." if len(code) > 100 else code
    print(f"DEBUG: Executing Code: {preview}")
    
    result = execution_service.execute_code(code)
    
    if result["status"] == "success":
        return result["output"]
    else:
        return f"Execution Error: {result['error']}"

def read_url(url: str) -> str:
    """Read the content of a webpage to get detailed information."""
    print(f"DEBUG: Reading URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text(separator='\n')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit length to avoid context overflow (approx 4000 chars)
        return text[:4000] + "\n...(content truncated)"
        
    except Exception as e:
        return f"Error reading URL: {str(e)}"

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for current events, news, or facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code to calculate math, process text, or solve logic puzzles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The python code to run"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Visit a specific URL to read its full content. Use this when search results are too short or vague.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to visit"
                    }
                },
                "required": ["url"]
            }
        }
    }
]
