resource "aws_secretsmanager_secret" "video_streaming_secrets" {
  name        = "video-streaming-v2-secrets-${random_id.bucket_suffix.hex}"
  description = "Secrets for Video Streaming V2 application"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

resource "random_password" "encryption_key" {
  length  = 32
  special = false
}

resource "random_password" "internal_api_key" {
  length  = 32
  special = false
}

resource "random_password" "external_api_key" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret_version" "video_streaming_secrets" {
  secret_id = aws_secretsmanager_secret.video_streaming_secrets.id
  secret_string = jsonencode({
    jwt_secret = random_password.jwt_secret.result
    cognito_client_secret = aws_cognito_user_pool_client.video_streaming_client.client_secret
    encryption_key = random_password.encryption_key.result
    api_keys = {
      internal = random_password.internal_api_key.result
      external = random_password.external_api_key.result
    }
    cognito_user_pool_id = aws_cognito_user_pool.video_streaming_v2.id
    cognito_client_id = aws_cognito_user_pool_client.video_streaming_client.id
    s3_bucket_name = aws_s3_bucket.video_streaming_v2.bucket
  })
}

output "secrets_manager_arn" {
  value = aws_secretsmanager_secret.video_streaming_secrets.arn
}