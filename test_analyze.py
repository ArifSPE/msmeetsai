#!/usr/bin/env python3
"""
Test analyze endpoint
"""
import requests
import json

test_request = {
    "scenario": "Customer wants a $8000 loan with credit score 720 and annual income $60000",
    "context": {
        "loan_amount": 8000,
        "credit_score": 720,
        "annual_income": 60000,
        "debt_to_income": 0.25,
        "customer_type": "existing"
    },
    "domain_hint": "finance",
    "category_hint": "loan_approval"
}

try:
    print("🧪 Testing /analyze endpoint...")
    response = requests.post(
        "http://localhost:8000/analyze",
        headers={"Content-Type": "application/json"},
        json=test_request,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error Response: {response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'response' in locals():
        print(f"Response text: {response.text}")