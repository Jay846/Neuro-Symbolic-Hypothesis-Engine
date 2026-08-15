import requests
from config import FEATHERLESS_API_URL, FEATHERLESS_API_KEY, DEFAULT_MODEL

def generate_equations(data_summary: str, domain_context: str = "", logs: list = None) -> list:
    """
    Generate candidate symbolic equations using Featherless AI.
    """
    # 1. Fetch live web research if context is available
    web_research = ""
    if domain_context and len(domain_context.strip()) >= 3:
        from engine.research_agent import fetch_web_research
        web_research = fetch_web_research(domain_context, logs)
        
    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""You are a senior quantitative researcher and mathematical scientist.
Your task is to generate 5 distinct candidate mathematical equations that could model the relationship in the provided dataset.
Target relationship description/summary:
{data_summary}

Domain Context (if any):
{domain_context}
"""
    if web_research:
        prompt += f"""
Web Research Context Scraped from Scientific/Financial Sites:
{web_research}
"""
    prompt += """
Return a JSON array of objects. Each object must have:
- "equation_str": The formula in SymPy-compatible Python syntax (e.g. "a * x + b * sin(x)"). Use variables like 'x' for input.
- "parameters": A list of parameter names used (e.g. ["a", "b"]).
- "reasoning": A brief explanation of why this functional form makes sense.

Response MUST be valid JSON only. Do not wrap in markdown blocks.
"""
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional mathematical modeling assistant. Output raw JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(f"{FEATHERLESS_API_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        
        # Clean potential markdown wrapping
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        import json
        return json.loads(content)
    except Exception as e:
        # Fallback to simple baseline functional forms if API call fails
        print(f"Featherless API call failed: {e}")
        return [
            {"equation_str": "a * x + b", "parameters": ["a", "b"], "reasoning": "Linear baseline"},
            {"equation_str": "a * x**2 + b * x + c", "parameters": ["a", "b", "c"], "reasoning": "Quadratic baseline"},
            {"equation_str": "a * exp(b * x) + c", "parameters": ["a", "b", "c"], "reasoning": "Exponential growth"}
        ]

def self_heal_equation(equation_str: str, error_message: str) -> dict:
    """
    Asks the LLM to correct an equation that threw a syntax or runtime error during execution.
    """
    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""The following equation generated previously returned an error during execution or parameter fitting:
Equation: {equation_str}
Error Message: {error_message}

Please correct the equation to ensure it is valid, SymPy-compatible, and avoids mathematical issues (like division by zero or negative base powers).
Return a JSON object with:
- "equation_str": Corrected equation string.
- "parameters": List of parameters.
- "explanation": What you corrected.
"""
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "You are a mathematical code repair assistant. Output raw JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(f"{FEATHERLESS_API_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        import json
        return json.loads(content)
    except Exception as e:
        print(f"Self-heal API call failed: {e}")
        return {"equation_str": "a * x + b", "parameters": ["a", "b"], "explanation": "Fallback to linear"}
