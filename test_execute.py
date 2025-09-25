#!/usr/bin/env python3
"""
Quick test for the execute endpoint
"""
import requests
import json

# Test data
test_request = {
    "scenario": "Customer wants a $5000 loan with credit score 680",
    "context": {
        "loan_amount": 5000,
        "credit_score": 680,
        "customer_type": "new"
    },
    "domain_hint": "finance"
}

try:
    print("🧪 Testing /execute endpoint...")
    response = requests.post(
        "http://localhost:8000/execute",
        headers={"Content-Type": "application/json"},
        json=test_request,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except requests.exceptions.ConnectionError:
    print("❌ Server not running at http://localhost:8000")
except requests.exceptions.Timeout:
    print("⏰ Request timed out")
except Exception as e:
    print(f"❌ Error: {e}")
    if hasattr(response, 'text'):
        print(f"Response text: {response.text}")