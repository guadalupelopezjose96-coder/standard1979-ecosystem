package standard1979.governance.workforce

import rego.v1

default allow := false

# 1. Validación de Cesión Presente de IP (17 U.S.C. § 101, DTSA 18 U.S.C. § 1836)
valid_ip_assignment if {
    input.contract.present_assignment == true
    input.contract.includes_ai_weights == true
    input.contract.dtsa_immunity_notice == true
}

# 2. Regla de los Cuatro Quintos de la EEOC (29 CFR Part 1607)
valid_eeoc_impact if {
    input.recruitment.adverse_impact_ratio >= 0.80
}

# 3. Gobernanza Criptográfica de Código (Fed. R. Evid. 902(14))
valid_crypto_identity if {
    input.operator.key_type == "Ed25519"
    input.operator.hardware_mfa == true
}

# 4. Asignación Inter-Compañía y Transfer Pricing (IRC § 482 / ASC 606)
valid_transfer_pricing if {
    input.intercompany.has_services_agreement == true
    input.intercompany.arm_length_margin >= 0.05
    input.intercompany.asc606_step_evaluation == true
}

# 5. Gobernanza de Agentes IA (ISO/IEC 42001 & C2PA v2.1)
valid_ai_workforce if {
    input.ai_agent.human_in_the_loop == true
    input.ai_agent.c2pa_manifest_present == true
    input.ai_agent.merkle_proof_sealed == true
}

# Decisión de Conformidad Global
allow if {
    valid_ip_assignment
    valid_eeoc_impact
    valid_crypto_identity
    valid_transfer_pricing
    valid_ai_workforce
}

deny contains msg if {
    not valid_ip_assignment
    msg := "VIOLACIÓN LEGAL: Contrato de trabajo carece de cesión presente de IP, pesos de IA o aviso DTSA § 1833(b)."
}

deny contains msg if {
    not valid_eeoc_impact
    msg := "VIOLACIÓN REGULATORIA: Proceso de selección algorítmica no supera la regla de los cuatro quintos (EEOC < 0.80)."
}

deny contains msg if {
    not valid_crypto_identity
    msg := "VIOLACIÓN DE SEGURIDAD: Operador no cuenta con llave Ed25519 o MFA de hardware (FIPS 140-3)."
}

deny contains msg if {
    not valid_transfer_pricing
    msg := "VIOLACIÓN FISCAL: Facturación inter-compañía incumple IRC § 482 (Arm's Length) o ASC 606."
}

deny contains msg if {
    not valid_ai_workforce
    msg := "VIOLACIÓN DE IA: Agente autónomo opera sin Human-in-the-Loop o carece de procedencia C2PA / Merkle."
}
