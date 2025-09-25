#!/bin/bash

echo "Testing confidence scores..."
echo "=========================================="

echo -e "\n1. Testing WITHOUT context (should return confidence > 0):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"scenario": "Customer wants to apply for a $50,000 loan with credit score 720"}' \
  | jq -r '"Overall Confidence: " + (.overall_confidence * 100 | tostring) + "%"'

echo -e "\n2. Testing WITH empty context (should return confidence > 0 now):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"scenario": "Customer wants to apply for a $50,000 loan with credit score 720", "context": {}}' \
  | jq -r '"Overall Confidence: " + (.overall_confidence * 100 | tostring) + "%"'

echo -e "\n3. Testing WITH actual context (should return confidence > 0 now):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"scenario": "Customer wants to apply for a $50,000 loan with credit score 720", "context": {"customer": {"credit_score": 720}}}' \
  | jq -r '"Overall Confidence: " + (.overall_confidence * 100 | tostring) + "%"'

echo -e "\nTest complete!"