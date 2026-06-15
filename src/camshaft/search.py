import re
import asyncio
import httpx
from html.parser import HTMLParser
from urllib.parse import quote_plus

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_script_or_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style"]:
            self.in_script_or_style = True

    def handle_endtag(self, tag):
        if tag in ["script", "style"]:
            self.in_script_or_style = False

    def handle_data(self, data):
        if not self.in_script_or_style:
            clean = data.strip()
            if clean:
                self.text.append(clean)

    def get_text(self):
        return " ".join(self.text)

async def search_duckduckgo_html(query: str, client: httpx.AsyncClient) -> str:
    """Native DuckDuckGo HTML snippet extraction (no 3rd party search packages)."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = await client.get(f"https://html.duckduckgo.com/html/?q={quote_plus(query)}", headers=headers, timeout=10.0)
        resp.raise_for_status()
        
        # Extremely basic regex extraction for the snippet text to avoid BS4 dependency
        results = []
        html = resp.text
        # DuckDuckGo HTML class for snippets is usually 'result__snippet'
        snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
        urls = re.findall(r'<a class="result__url" href="([^"]+)">', html, re.IGNORECASE)
        
        for i, snippet in enumerate(snippets[:3]):
            clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            url = urls[i] if i < len(urls) else "Unknown"
            results.append(f"URL: {url}\nSnippet: {clean_snippet}")
            
        if not results:
            return "No snippets found."
        return "\n\n".join(results)
    except Exception as e:
        return f"Search failed: {e}"

async def download_and_extract(url: str, client: httpx.AsyncClient) -> str:
    """Native HTML text extraction (no BeautifulSoup)."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = await client.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
        extractor = TextExtractor()
        extractor.feed(resp.text)
        return extractor.get_text()[:10000] # Limit tokens
    except Exception as e:
        return f"Failed to download: {e}"

async def perform_deep_search(query: str, target_llm_url: str) -> str:
    """
    Agentic ReAct loop built natively. 
    It evaluates snippets and only downloads URLs when explicitly instructed.
    """
    print(f"\n[Deep Search] Initiating Agentic Loop for: '{query}'")
    
    system_prompt = (
        "You are an elite research agent. You must cross-reference information and find verified facts. "
        "You have two tools:\n"
        "1. SEARCH(query) - Returns snippets from the web.\n"
        "2. DOWNLOAD(url) - Downloads full text of a specific URL.\n\n"
        "Rules:\n"
        "- If you need to search, output exactly: SEARCH(your query)\n"
        "- Evaluate the snippets. DO NOT download blindly. ONLY download if a snippet is highly relevant but incomplete.\n"
        "- If you need to download, output exactly: DOWNLOAD(url)\n"
        "- When you have verified facts to answer the user's requirement, output exactly: FINAL: <your verified answer>\n"
        "Always wait for the tool output before making your next move."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Requirement: {query}"}
    ]
    
    async with httpx.AsyncClient() as client:
        for step in range(5): # Max 5 steps to prevent infinite loops
            body = {"model": "local-model", "messages": messages, "temperature": 0.0}
            try:
                resp = await client.post(f"{target_llm_url}/chat/completions", json=body, timeout=60.0)
                resp.raise_for_status()
            except Exception as e:
                print(f"[Deep Search] Local LLM failed: {e}")
                return ""
                
            reply = resp.json()["choices"][0]["message"]["content"].strip()
            print(f"[Agent] {reply}")
            messages.append({"role": "assistant", "content": reply})
            
            if reply.startswith("FINAL:"):
                return reply.replace("FINAL:", "").strip()
                
            elif reply.startswith("SEARCH("):
                search_term = reply[7:-1].strip("'\"")
                print(f"[*] Executing Search: {search_term}")
                snippets = await search_duckduckgo_html(search_term, client)
                messages.append({"role": "user", "content": f"Search Results:\n{snippets}"})
                
            elif reply.startswith("DOWNLOAD("):
                url = reply[9:-1].strip("'\"")
                print(f"[*] Executing Download: {url}")
                page_text = await download_and_extract(url, client)
                messages.append({"role": "user", "content": f"Page Content:\n{page_text}"})
            else:
                messages.append({"role": "user", "content": "Error: You must output SEARCH, DOWNLOAD, or FINAL."})
                
    return "Agentic search timed out before finding a final answer."
