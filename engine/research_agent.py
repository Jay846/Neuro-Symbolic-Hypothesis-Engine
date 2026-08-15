import requests
from config import FIRECRAWL_API_KEY

def fetch_web_research(domain_context: str, logs: list = None) -> str:
    """
    Search the web using Firecrawl to fetch papers and formula references
    related to the domain context.
    """
    if not FIRECRAWL_API_KEY:
        msg = "Firecrawl API key not set. Skipping web research..."
        print(msg)
        if logs is not None:
            logs.append(msg)
        return ""
    
    if not domain_context or len(domain_context.strip()) < 3:
        return ""
        
    msg = f"Initiating Firecrawl web search for context: '{domain_context}'..."
    print(msg)
    if logs is not None:
        logs.append(msg)
        
    # Firecrawl V2 Search Endpoint
    url = "https://api.firecrawl.dev/v2/search"
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    query = f"mathematical model formulas equations for {domain_context}"
    payload = {
        "query": query,
        "limit": 2,
        "scrapeOptions": {
            "formats": ["markdown"]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        response.raise_for_status()
        res_json = response.json()
        
        if not res_json.get("success"):
            msg = f"Firecrawl search response reported failure: {res_json}"
            print(msg)
            if logs is not None:
                logs.append(msg)
            return ""
            
        data = res_json.get("data", {})
        web_results = data.get("web", []) if isinstance(data, dict) else []
        
        research_docs = []
        for idx, doc in enumerate(web_results):
            title = doc.get("title", "Untitled Document")
            source_url = doc.get("url", "")
            markdown = doc.get("markdown", "")
            
            # Slice to 3000 chars to stay within reasonable model prompt context lengths
            truncated_md = markdown[:3000]
            research_docs.append(f"Source {idx+1}: {title} ({source_url})\n---\n{truncated_md}\n---\n")
            
        if not research_docs:
            msg = "Firecrawl search did not return any web results."
            if logs is not None:
                logs.append(msg)
            return ""
            
        msg = f"Firecrawl search successful! Scraping completed for {len(research_docs)} sources."
        print(msg)
        if logs is not None:
            logs.append(msg)
            
        return "\n".join(research_docs)
    except Exception as e:
        msg = f"Firecrawl query failed: {e}"
        print(msg)
        if logs is not None:
            logs.append(msg)
        return ""
