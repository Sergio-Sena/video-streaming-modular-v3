resource "aws_cognito_user_pool" "video_streaming_v2" {
  name = "video-streaming-v2-users"
  
  mfa_configuration = "ON"
  
  software_token_mfa_configuration {
    enabled = true
  }
  
  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
  
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }
  
  auto_verified_attributes = ["email"]
  
  tags = {
    Environment = "production"
    Project     = "video-streaming-v2"
  }
}

resource "aws_cognito_user_pool_client" "video_streaming_client" {
  name         = "video-streaming-v2-client"
  user_pool_id = aws_cognito_user_pool.video_streaming_v2.id
  
  generate_secret = true
  
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
  
  supported_identity_providers = ["COGNITO"]
  
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }
  
  access_token_validity  = 24
  id_token_validity      = 24
  refresh_token_validity = 30
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.video_streaming_v2.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.video_streaming_client.id
}

output "cognito_client_secret" {
  value = aws_cognito_user_pool_client.video_streaming_client.client_secret
  sensitive = true
}