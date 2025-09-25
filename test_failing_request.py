#!/usr/bin/env python3
"""
Test the exact request that was failing
"""
import requests
import json

test_request = {
    "scenario": "Execute loan approval for qualified customer",
    "rules": [
        {
            "id": "finance_loan_001",
            "name": "Basic Credit Check",
            "action": "approve_basic_review",
            "parameters": {
                "loan_amount": 8000,
                "credit_score": 720
            }
        }
    ],
    "context": {
        "customer_id": "CUST-789",
        "loan_amount": 8000,
        "credit_score": 720,
        "application_id": "LOAN-2024-001"
    }
}

try:
    print("🧪 Testing the failing request...")
    response = requests.post(
        "http://localhost:8000/execute",
        headers={"Content-Type": "application/json"},
        json=test_request,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ SUCCESS! Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Error Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'response' in locals():
        print(f"Response text: {response.text}")