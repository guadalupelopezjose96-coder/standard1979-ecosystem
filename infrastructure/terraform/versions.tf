terraform {
  required_version = ">= 1.8.0"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.40.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.65.0"
    }
  }
}
