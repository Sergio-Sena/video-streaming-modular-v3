# API Gateway Configuration - Auth Service v3

## API Details
- **API ID**: vyo27kghrh
- **API Name**: auth-service-v3-api
- **Stage**: prod
- **Base URL**: https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod

## Endpoints

### POST /auth/register
- **URL**: https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod/auth/register
- **Method**: POST
- **Purpose**: User registration with MFA setup
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```

### POST /auth/login
- **URL**: https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod/auth/login
- **Method**: POST
- **Purpose**: User login with MFA verification
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "mfa_code": "123456"
  }
  ```

### POST /auth/verify
- **URL**: https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod/auth/verify
- **Method**: POST
- **Purpose**: Verify JWT token validity
- **Body**: 
  ```json
  {
    "token": "jwt_token_here"
  }
  ```

### POST /auth/refresh
- **URL**: https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod/auth/refresh
- **Method**: POST
- **Purpose**: Refresh JWT token
- **Body**: 
  ```json
  {
    "refresh_token": "refresh_token_here"
  }
  ```

## Lambda Integration
- **Function**: auth-service-v3
- **ARN**: arn:aws:lambda:us-east-1:969430605054:function:auth-service-v3
- **Integration Type**: AWS_PROXY
- **Timeout**: 29 seconds

## Deployment
- **Latest Deployment ID**: rhd8sx
- **Stage**: prod
- **Created**: 2025-08-30T19:12:25-03:00
- **Previous Deployment**: 1cf7k1 (2025-08-30T18:53:45-03:00)

## Current Status
- **API Gateway**: ✅ Configured with all endpoints
- **Lambda Integration**: ✅ Connected to auth-service-v3
- **Permissions**: ✅ API Gateway can invoke Lambda
- **Lambda Function**: ⚠️ Code deployment issues (null bytes error)
- **Endpoints Status**: ⚠️ Returning 500 Internal Server Error

## Testing Commands
```bash
# Test register endpoint
curl -X POST https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test login endpoint
curl -X POST https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","mfa_code":"123456"}'
```