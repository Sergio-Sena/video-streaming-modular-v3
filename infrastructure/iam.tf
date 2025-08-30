# Auth Service Role
resource "aws_iam_role" "auth_service_role" {
  name = "video-streaming-v2-auth-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "auth_service_policy" {
  name = "auth-service-policy"
  role = aws_iam_role.auth_service_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "cognito-idp:InitiateAuth",
          "cognito-idp:RespondToAuthChallenge",
          "cognito-idp:AssociateSoftwareToken",
          "cognito-idp:VerifySoftwareToken",
          "cognito-idp:SetUserMFAPreference",
          "cognito-idp:AdminCreateUser",
          "cognito-idp:AdminSetUserPassword",
          "cognito-idp:AdminGetUser"
        ]
        Resource = aws_cognito_user_pool.video_streaming_v2.arn
      },
      {
        Effect = "Allow"
        Action = "secretsmanager:GetSecretValue"
        Resource = aws_secretsmanager_secret.video_streaming_secrets.arn
      }
    ]
  })
}

# Upload Service Role
resource "aws_iam_role" "upload_service_role" {
  name = "video-streaming-v2-upload-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "upload_service_policy" {
  name = "upload-service-policy"
  role = aws_iam_role.upload_service_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:AbortMultipartUpload",
          "s3:ListMultipartUploadParts",
          "s3:ListBucketMultipartUploads"
        ]
        Resource = [
          aws_s3_bucket.video_streaming_v2.arn,
          "${aws_s3_bucket.video_streaming_v2.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = "secretsmanager:GetSecretValue"
        Resource = aws_secretsmanager_secret.video_streaming_secrets.arn
      }
    ]
  })
}

# Video Service Role
resource "aws_iam_role" "video_service_role" {
  name = "video-streaming-v2-video-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "video_service_policy" {
  name = "video-service-policy"
  role = aws_iam_role.video_service_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetObjectMetadata"
        ]
        Resource = [
          aws_s3_bucket.video_streaming_v2.arn,
          "${aws_s3_bucket.video_streaming_v2.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = "secretsmanager:GetSecretValue"
        Resource = aws_secretsmanager_secret.video_streaming_secrets.arn
      }
    ]
  })
}

# Outputs
output "auth_service_role_arn" {
  value = aws_iam_role.auth_service_role.arn
}

output "upload_service_role_arn" {
  value = aws_iam_role.upload_service_role.arn
}

output "video_service_role_arn" {
  value = aws_iam_role.video_service_role.arn
}