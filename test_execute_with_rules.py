#!/usr/bin/env python3
"""
Test execute endpoint with explicit rules
"""
import requests
import json

# Test with explicit rules
test_request = {
    "scenario": "Execute loan approval for qualified customer",
    "context": {
        "customer_id": "CUST-789",
        "loan_amount": 5000,
        "credit_score": 680,
        "application_id": "LOAN-2024-001"
    },
    "rules": [
        {
            "id": "finance_loan_001",
            "name": "Basic Credit Check",
            "description": "Basic credit score validation",
            "condition": "credit_score >= 650",
            "action": "approve_basic_review",
            "priority": 2,
            "parameters": {
                "loan_amount": 5000,
                "credit_score": 680
            }
        }
    ]
}

try:
    print("🧪 Testing /execute endpoint with explicit rules...")
    response = requests.post(
        "http://localhost:8000/execute",
        headers={"Content-Type": "application/json"},
        json=test_request,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'response' in locals():
        print(f"Response text: {response.text}")