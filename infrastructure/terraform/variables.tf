variable "cloudflare_account_id" {
  description = "ID de la cuenta corporativa de Cloudflare bajo Standard 1979 Holdings, LLC"
  type        = string
}

variable "aws_region" {
  description = "Región principal de AWS en EE. UU."
  type        = string
  default     = "us-east-1"
}

variable "ecosystem_domains" {
  description = "Mapa oficial de los 6 dominios de Standard 1979 Holdings, LLC y sus unidades operativas"
  type = map(object({
    opco_entity = string
    tier        = string
    dkim_pubkey = string
  }))
  default = {
    "standard1979.com" = {
      opco_entity = "Standard_1979_Holdings_LLC"
      tier        = "holding"
      dkim_pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1979holdingkey..."
    }
    "auraintelcore.com" = {
      opco_entity = "Aura_Technologies_Operating_LLC"
      tier        = "ai_core"
      dkim_pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAauracorekey..."
    }
    "auratetrax.com" = {
      opco_entity = "Aura_Technologies_Operating_LLC"
      tier        = "modular_paas"
      dkim_pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAauratetraxkey..."
    }
    "auraintelstudios3d.com" = {
      opco_entity = "Aura_Technologies_Operating_LLC"
      tier        = "3d_gpu_studio"
      dkim_pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAaura3dkey..."
    }
    "fourphonix.com" = {
      opco_entity = "Phonix_Communications_Operating_LLC"
      tier        = "telecom_voice"
      dkim_pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAfourphonixkey..."
    }
    "prophonix.com" = {
      opco_entity = "Phonix_Communications_Operating_LLC"
      tier        = "b2b_ucaas"
      dkim_pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAprophonixkey..."
    }
  }
}
