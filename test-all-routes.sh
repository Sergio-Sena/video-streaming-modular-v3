#!/bin/bash

BASE_URL="https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
TOKEN="eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzdWIiOiAic2VuYW5ldHdvcmtlckBnbWFpbC5jb20iLCAidXNlcl9pZCI6ICJ1c2VyLXNlcmdpby1zZW5hIiwgIm5hbWUiOiAiU2VyZ2lvIFNlbmEiLCAiZXhwIjogMTc1Njg0MTcxOSwgImlhdCI6IDE3NTY3NTUzMTl9.cu_i-Ne6ptq0il-qgdLJ9FM7fXvll7GtUv7JTmWqcqY"

echo "🧪 TESTANDO TODAS AS ROTAS DA API..."
echo "=================================="

echo "✅ 1. Health Check:"
curl -s -w "Status: %{http_code}\n" "$BASE_URL/health" | head -1

echo -e "\n✅ 2. Login:"
curl -s -w "Status: %{http_code}\n" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"senanetworker@gmail.com","password":"sergiosena"}' | head -1

echo -e "\n✅ 3. Forgot Password:"
curl -s -w "Status: %{http_code}\n" -X POST "$BASE_URL/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email":"senanetworker@gmail.com"}' | head -1

echo -e "\n✅ 4. User Profile:"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/user/profile" \
  -H "Authorization: Bearer $TOKEN" | head -1

echo -e "\n✅ 5. User Storage:"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/user/storage" \
  -H "Authorization: Bearer $TOKEN" | head -1

echo -e "\n✅ 6. List Files:"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/files" \
  -H "Authorization: Bearer $TOKEN" | head -1

echo -e "\n✅ 7. Upload File (URL):"
curl -s -w "Status: %{http_code}\n" -X POST "$BASE_URL/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | head -1

echo -e "\n✅ 8. Download File (404 expected):"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/files/test-id/download" \
  -H "Authorization: Bearer $TOKEN" | head -1

echo -e "\n✅ 9. Delete File (404 expected):"
curl -s -w "Status: %{http_code}\n" -X DELETE "$BASE_URL/files/test-id" \
  -H "Authorization: Bearer $TOKEN" | head -1

echo -e "\n✅ 10. Validate Reset Token (400 expected):"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/auth/validate-reset-token" | head -1

echo -e "\n✅ 11. Unauthorized Test (401 expected):"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/user/profile" | head -1

echo -e "\n✅ 12. Not Found Test (404 expected):"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/invalid-route" | head -1

echo -e "\n🎉 TESTE COMPLETO!"