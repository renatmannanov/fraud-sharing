"""
eStaff API Explorer
Connects to eStaff test API and discovers available data structure.
Based on OpenAPI spec: Bearer auth, POST endpoints.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ESTAFF_API_URL", "").rstrip("/")
API_KEY = os.getenv("ESTAFF_API_KEY", "")

if not BASE_URL.startswith("http"):
    BASE_URL = f"http://{BASE_URL}"

API_URL = f"{BASE_URL}/api"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

print(f"API URL: {API_URL}")
print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print("=" * 60)


def api_post(path, body, description):
    """Make a POST request and print the result."""
    url = f"{API_URL}{path}"
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print(f"POST {url}")
    print(f"Body: {json.dumps(body, ensure_ascii=False)}")
    print("-" * 60)

    try:
        resp = requests.post(url, headers=HEADERS, json=body, timeout=15)
        print(f"Status: {resp.status_code}")

        try:
            data = resp.json()
            text = json.dumps(data, ensure_ascii=False, indent=2)
            if len(text) > 5000:
                print(text[:5000])
                print(f"\n... (truncated, total {len(text)} chars)")
            else:
                print(text)
            return data
        except json.JSONDecodeError:
            print(f"Response (text): {resp.text[:2000]}")
            return None
    except requests.ConnectionError as e:
        print(f"Connection error: {e}")
        return None
    except requests.Timeout:
        print("Timeout (15s)")
        return None


# --- 1. Find candidates (small batch to see structure) ---
print("\n### PHASE 1: Find candidates ###")

# Try finding with empty filter first to see what comes back
result = api_post("/candidate/find", {
    "filter": {},
    "field_names": {}
}, "Find candidates — empty filter, empty field_names")

# Try with field_names to get all fields
result2 = api_post("/candidate/find", {
    "filter": {},
    "field_names": {
        "lastname": True,
        "firstname": True,
        "middlename": True,
        "birth_date": True,
        "mobile_phone": True,
        "email": True,
        "prev_jobs": True,
        "inet_uid": True,
        "source_id": True,
        "desired_position_name": True,
        "exp_years": True,
    }
}, "Find candidates — with field_names for key fields")


# --- 2. If we got candidates, get details for the first one ---
print("\n### PHASE 2: Get candidate details ###")

if result2 and isinstance(result2, dict):
    # Try to find candidate IDs in the response
    candidates = result2.get("candidates", result2.get("data", result2.get("items", [])))
    if isinstance(candidates, list) and len(candidates) > 0:
        first = candidates[0]
        cand_id = first.get("id") or first.get("candidate_id")
        if cand_id:
            api_post("/candidate/get", {
                "candidate": {"id": cand_id},
                "field_names": {},
                "options": {"use_full_data": True}
            }, f"Get full candidate data for id={cand_id}")
        else:
            print(f"First candidate keys: {list(first.keys())}")
    else:
        print(f"Response structure: {list(result2.keys()) if isinstance(result2, dict) else type(result2)}")
else:
    print("No results from find, trying get with id=1")
    api_post("/candidate/get", {
        "candidate": {"id": 1},
        "field_names": {},
        "options": {"use_full_data": True}
    }, "Get candidate id=1 with full data")


print("\n" + "=" * 60)
print("DONE.")
