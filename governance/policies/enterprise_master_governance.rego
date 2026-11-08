package standard1979.governance.master

import rego.v1

default allow := false

# 1. Validación de Ciclo de Vida DevSecOps & Compilación
valid_build_and_supply_chain if {
    input.build.deterministic == true
    input.build.sbom_formats[_] == "CycloneDX-1.6"
    input.build.sbom_formats[_] == "SPDX-3.0"
    count(prohibited_licenses) == 0
    input.artifact.cosign_signed == true
}

# Detección de licencias restrictivas no compatibles con código privativo
prohibited_licenses contains lic if {
    some lic in input.build.detected_licenses
    prohibited_set := {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL", "EUPL-1.2"}
    prohibited_set[lic]
}

# 2. Validación de Seguridad e Infraestructura Zero-Trust
valid_infrastructure_hardening if {
    input.runtime.distroless == true
    input.runtime.read_only_rootfs == true
    input.runtime.run_as_non_root == true
    input.network.mtls_enabled == true
    input.network.tls_version == "TLSv1.3"
    input.crypto.hardware_fips_level >= 2
}

# 3. Gobernanza de Inteligencia Artificial (ISO 42001 & HITL)
valid_ai_governance if {
    input.ai_system.iso42001_registered == true
    input.ai_system.c2pa_manifest_present == true
    input.ai_system.merkle_proof_verified == true
    human_in_the_loop_verified
}

# HITL obligatorio para operaciones de producción o financieras
human_in_the_loop_verified if {
    input.operation.criticality == "HIGH"
    input.operation.human_supervisor_signed == true
}

human_in_the_loop_verified if {
    input.operation.criticality != "HIGH"
}

# 4. Cumplimiento Financiero y Precios de Transferencia (ASC 606 & IRC § 482)
valid_financial_compliance if {
    input.financial.asc606_five_step_applied == true
    input.intercompany.royalty_percentage_aura >= 0.15
    input.intercompany.royalty_percentage_phonix >= 0.10
    input.tax.fl_cst_compliant == true
}

# 5. Defensa Patrimonial y DRP
valid_disaster_recovery if {
    input.drp.vault_encrypted_aes256 == true
    input.drp.pbkdf2_iterations >= 600000
    input.drp.shamir_quorum_threshold == 3
    input.drp.shamir_total_shares == 5
}

# Regla Maestra de Autorización
allow if {
    valid_build_and_supply_chain
    valid_infrastructure_hardening
    valid_ai_governance
    valid_financial_compliance
    valid_disaster_recovery
}

# Reglas de Notificación de Incumplimiento
deny contains msg if {
    not valid_build_and_supply_chain
    msg := "DEVSECOPS VIOLATION: Pipeline no reproducible, SBOM incompleto, artefacto sin firma Cosign o presencia de licencias GPL/AGPL."
}

deny contains msg if {
    not valid_infrastructure_hardening
    msg := "ZERO-TRUST VIOLATION: Contenedor no distroless, sistema de archivos mutable, o mTLS FIPS 140-3 ausente."
}

deny contains msg if {
    not valid_ai_governance
    msg := "AI GOVERNANCE VIOLATION: Falta de registro ISO 42001, ausencia de sello C2PA v2.1/Merkle, o falta de aprobación HITL en acción crítica."
}

deny contains msg if {
    not valid_financial_compliance
    msg := "FINANCIAL/TAX VIOLATION: Desviación en regalías IRC § 482 (Aura < 15%, Phonix < 10%) o incumplimiento ASC 606 / FL CST."
}

deny contains msg if {
    not valid_disaster_recovery
    msg := "RESILIENCE VIOLATION: Bóveda DRP no configurada con AES-256 (600k iteraciones) o esquema de Shamir 3-de-5 no cumplido."
}
