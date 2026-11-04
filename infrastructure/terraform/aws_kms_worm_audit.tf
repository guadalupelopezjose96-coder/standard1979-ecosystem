provider "aws" {
  region = var.aws_region
}

# 1. Llave Maestra KMS con Rotación Anual Automática (FIPS 140-3 / AES-256-GCM)
resource "aws_kms_key" "ecosystem_audit_kms" {
  description             = "Master KMS Key for Standard 1979 Holdings, Aura OpCo and Phonix OpCo WORM Audit Logs & CPNI"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  multi_region            = true

  tags = {
    Holding    = "Standard_1979_Holdings_LLC"
    Compliance = "SOC2_ISO27001_ISO42001_FCC_CPNI_TCPA"
  }
}

resource "aws_kms_alias" "ecosystem_audit_kms_alias" {
  name          = "alias/standard1979-ecosystem-worm-kms"
  target_key_id = aws_kms_key.ecosystem_audit_kms.key_id
}

# 2. Buckets S3 con Object Lock en Modo COMPLIANCE (WORM Inmutable por 7 años) para cada Dominio
resource "aws_s3_bucket" "worm_audit_buckets" {
  for_each            = var.ecosystem_domains
  bucket              = "s1979-worm-audit-${replace(each.key, ".", "-")}"
  object_lock_enabled = true

  tags = {
    Domain    = each.key
    Entity    = each.value.opco_entity
    Tier      = each.value.tier
    Retention = "7_Years_WORM_Compliance"
  }
}

resource "aws_s3_bucket_versioning" "worm_versioning" {
  for_each = aws_s3_bucket.worm_audit_buckets
  bucket   = each.value.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "worm_encryption" {
  for_each = aws_s3_bucket.worm_audit_buckets
  bucket   = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.ecosystem_audit_kms.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "worm_private_lock" {
  for_each                = aws_s3_bucket.worm_audit_buckets
  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_object_lock_configuration" "worm_7_years_lock" {
  for_each = aws_s3_bucket.worm_audit_buckets
  bucket   = each.value.id

  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = 2555 # 7 años (Requisito Fiscal IRS, Auditoría SOC 2 y TCPA/CPNI)
    }
  }
}
