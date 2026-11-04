# 1. Creación de Zonas DNS para los 6 Dominios
resource "cloudflare_zone" "domains" {
  for_each   = var.ecosystem_domains
  account_id = var.cloudflare_account_id
  zone       = each.key
  plan       = "enterprise"
  type       = "full"
}

# 2. Activación de DNSSEC Criptográfico en los 6 Dominios
resource "cloudflare_zone_dnssec" "dnssec" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id
}

# 3. Endurecimiento TLS 1.3 Estricto, HSTS Preload y Zero Trust en los 6 Dominios
resource "cloudflare_zone_settings_override" "tls_hardening" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id

  settings {
    ssl                      = "strict"
    min_tls_version          = "1.3"
    tls_1_3                  = "zrt"
    always_use_https         = "on"
    automatic_https_rewrites = "on"
    http3                    = "on"
    brotli                   = "on"
    security_level           = "high"
    opportunistic_encryption = "on"

    security_header {
      enabled            = true
      max_age            = 63072000
      include_subdomains = true
      preload            = true
      nosniff            = true
    }
  }
}

# 4. Registros SPF Estricto (-all) para los 6 Dominios
resource "cloudflare_record" "spf" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id
  name     = "@"
  type     = "TXT"
  content  = "v=spf1 include:_spf.google.com include:amazonses.com -all"
  ttl      = 3600
}

# 5. Registros DKIM (RSA 2048-bit) para los 6 Dominios
resource "cloudflare_record" "dkim" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id
  name     = "s1979._domainkey"
  type     = "TXT"
  content  = "v=DKIM1; k=rsa; p=${var.ecosystem_domains[each.key].dkim_pubkey}"
  ttl      = 3600
}

# 6. Registros DMARC en Modo Cuarentena/Rechazo Total (p=reject) en los 6 Dominios
resource "cloudflare_record" "dmarc" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id
  name     = "_dmarc"
  type     = "TXT"
  content  = "v=DMARC1; p=reject; sp=reject; pct=100; adkim=s; aspf=s; rua=mailto:dmarc-rua@standard1979.com; ruf=mailto:dmarc-ruf@standard1979.com; fo=1"
  ttl      = 3600
}

# 7. Registros CAA (Certification Authority Authorization) restringiendo emisión de SSL
resource "cloudflare_record" "caa_letsencrypt" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id
  name     = "@"
  type     = "CAA"
  ttl      = 3600
  data {
    flags = 0
    tag   = "issue"
    value = "letsencrypt.org"
  }
}

resource "cloudflare_record" "caa_digicert" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id
  name     = "@"
  type     = "CAA"
  ttl      = 3600
  data {
    flags = 0
    tag   = "issue"
    value = "digicert.com"
  }
}

resource "cloudflare_record" "caa_iodef" {
  for_each = cloudflare_zone.domains
  zone_id  = each.value.id
  name     = "@"
  type     = "CAA"
  ttl      = 3600
  data {
    flags = 0
    tag   = "iodef"
    value = "mailto:security-soc@standard1979.com"
  }
}

# 8. Reglas WAF Enterprise: Bloqueo de Jurisdicciones Sancionadas OFAC / BIS y Protección API
resource "cloudflare_ruleset" "waf_ofac_and_owasp" {
  for_each    = cloudflare_zone.domains
  zone_id     = each.value.id
  name        = "Standard1979-OFAC-and-API-Hardening"
  description = "Bloqueo de países sancionados OFAC/EAR y protección de endpoints de IA y SIP WebRTC"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  rules {
    action      = "block"
    expression  = "(ip.geoip.country in {\"CU\" \"IR\" \"KP\" \"SY\" \"RU\"})"
    description = "Cumplimiento obligatorio OFAC / BIS Export Administration Regulations (EAR)"
    enabled     = true
  }

  rules {
    action      = "block"
    expression  = "(http.request.uri.path contains \"/v1/secure-inference\" and not http.request.method in {\"POST\"})"
    description = "Protección estricta de métodos HTTP en el AI Security Gateway"
    enabled     = true
  }
}
