#!/usr/bin/env python3
"""
Quick test script to verify LLM is responding correctly.
Run this after: docker compose --env-file .env.dev up -d

Usage: python test_llm_response.py
"""

import requests
import json
import os
import sys
import time

def test_llm():
    llm_host = os.getenv("LLM_HOST", "http://llm:80")
    test_query = "What grows well with 8 hours of sun?"
    
    print("="*80)
    print("Testing LLM Response Pipeline")
    print("="*80)
    print(f"LLM Host: {llm_host}")
    print(f"Test Query: '{test_query}'")
    print()
    
    # Build prompt (matching db.py)
    prompt = f"""Task: Extract plant care requirements from the user's gardening query.

Examples:
- Query: "I need full sun plants" → {{"sun_requirement": "full sun", "water_needs": null, "hardiness_zones": null}}
- Query: "Show me drought tolerant plants" → {{"sun_requirement": null, "water_needs": "low", "hardiness_zones": null}}
- Query: "What grows in zone 5?" → {{"sun_requirement": null, "water_needs": null, "hardiness_zones": "5"}}

User Query: "{test_query}"

Extract requirements as JSON. Use null for missing fields. Return ONLY the JSON, nothing else:
{{"""
    
    # Step 1: Send request
    print("[1] Sending request to LLM...")
    print(f"    Endpoint: {llm_host}/generate")
    print(f"    Prompt length: {len(prompt)} chars")
    
    try:
        response = requests.post(
            f"{llm_host}/generate",
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "top_p": 0.95
                }
            },
            timeout=60
        )
    except requests.exceptions.ConnectionError:
        print(f"    ❌ Connection failed! Is LLM running at {llm_host}?")
        print(f"    Try: docker compose --env-file .env.dev up -d llm")
        sys.exit(1)
    except Exception as e:
        print(f"    ❌ Request failed: {e}")
        sys.exit(1)
    
    print(f"    ✅ Got response (status: {response.status_code})")
    print()
    
    # Step 2: Parse raw response
    print("[2] Parsing raw response...")
    try:
        result = response.json()
        print(f"    ✅ Valid JSON response")
        print(f"    Response type: {type(result)}")
        print(f"    Response structure: {list(result[0].keys()) if isinstance(result, list) else list(result.keys())}")
    except json.JSONDecodeError:
        print(f"    ❌ Invalid JSON!")
        print(f"    Raw: {response.text[:200]}")
        sys.exit(1)
    print()
    
    # Step 3: Extract generated text
    print("[3] Extracting generated text...")
    generated_text = result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "")
    response_text = generated_text[len(prompt):].strip()
    
    print(f"    Generated text length: {len(generated_text)} chars")
    print(f"    Prompt length: {len(prompt)} chars")
    print(f"    Response text (after prompt): {len(response_text)} chars")
    print(f"    Response text: '{response_text}'")
    print()
    
    # Step 4: Parse JSON
    print("[4] Parsing extracted JSON...")
    
    if not response_text:
        print(f"    ❌ Empty response!")
        sys.exit(1)
    
    # Complete JSON if needed
    if not response_text.endswith("}"):
        response_text += "}"
        print(f"    ℹ️  Added closing brace")
    
    # Extract JSON
    if "{" not in response_text:
        print(f"    ❌ No JSON braces found!")
        sys.exit(1)
    
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    json_str = response_text[json_start:json_end]
    
    print(f"    Found JSON: {json_str}")
    
    try:
        filters = json.loads(json_str)
        print(f"    ✅ Valid JSON!")
        print(f"    Parsed filters: {filters}")
    except json.JSONDecodeError as e:
        print(f"    ❌ Invalid JSON: {e}")
        sys.exit(1)
    print()
    
    # Step 5: Remove null values (matching db.py)
    print("[5] Cleaning filters (removing null values)...")
    filters = {k: v for k, v in filters.items() if v is not None}
    print(f"    ✅ Cleaned filters: {filters}")
    print()
    
    # Success!
    print("="*80)
    print("✅ LLM Response Pipeline Working Correctly!")
    print("="*80)
    print()
    print("Test Results:")
    print(f"  - LLM reachable: Yes")
    print(f"  - Response format valid: Yes")
    print(f"  - JSON parsing works: Yes")
    print(f"  - Extracted filters: {filters}")
    print()
    print("The filter extraction pipeline is ready!")

if __name__ == "__main__":
    test_llm()
