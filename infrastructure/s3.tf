resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "video_streaming_v2" {
  bucket = "video-streaming-v2-${random_id.bucket_suffix.hex}"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "video_streaming_v2" {
  bucket = aws_s3_bucket.video_streaming_v2.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "video_streaming_v2" {
  bucket = aws_s3_bucket.video_streaming_v2.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "video_streaming_v2" {
  bucket = aws_s3_bucket.video_streaming_v2.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "s3_bucket_name" {
  value = aws_s3_bucket.video_streaming_v2.bucket
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.video_streaming_v2.arn
}