package standard1979.governance.gemini

import rego.v1

default allow := false

# 1. Validación de Canal Corporativo y Privacidad Cloud
valid_cloud_channel if {
    input.transport.provider == "google_cloud_vertex_ai"
    input.transport.private_service_connect == true
    input.transport.customer_data_training_disabled == true
    input.transport.cmek_fips_level >= 3
}

# 2. Endurecimiento de Entradas y Estructura Anti-Inyección (LLM01 / LLM07)
valid_input_structure if {
    input.prompt.system_instruction_isolated == true
    input.prompt.user_input_xml_encapsulated == true
    count(detected_injection_risks) == 0
}

detected_injection_risks contains risk if {
    some risk in input.security.detected_anomalies
    blocked_risks := {"PROMPT_INJECTION_DIRECT", "SYSTEM_PROMPT_EXTRACTION", "JAILBREAK_EVASION"}
    blocked_risks[risk]
}

# 3. Anonimización y Privacidad DLP (GDPR / CCPA / FDBR)
valid_data_privacy if {
    input.security.dlp_inspection_completed == true
    input.security.unredacted_pii_count == 0
    input.security.fpe_tokenization_applied == true
}

# 4. Tipado de Salida y Aislamiento de Ejecución (LLM02)
valid_output_contract if {
    input.response_format.enforce_json_schema == true
    input.response_format.schema_validated == true
    input.runtime.sandbox_isolated == true
}

# 5. Control de Agencia y Human-in-the-Loop (LLM06)
valid_agency_governance if {
    input.execution.criticality == "CRITICAL"
    input.execution.hitl_ed25519_signed == true
}

valid_agency_governance if {
    input.execution.criticality != "CRITICAL"
}

# 6. Evidencia Forense y Notarización Criptográfica (Fed. R. Evid. 902 / C2PA)
valid_cryptographic_audit if {
    input.audit.c2pa_manifest_generated == true
    input.audit.merkle_leaf_inserted == true
    input.audit.rfc3161_timestamp_present == true
}

# 7. Cumplimiento Financiero y Precios de Transferencia (ASC 606 / IRC § 482)
valid_finops_allocation if {
    input.finops.token_accounting_enabled == true
    input.finops.cost_center_assigned == true
    input.finops.intercompany_royalty_rate >= 0.10
}

# Regla Maestra de Autorización
allow if {
    valid_cloud_channel
    valid_input_structure
    valid_data_privacy
    valid_output_contract
    valid_agency_governance
    valid_cryptographic_audit
    valid_finops_allocation
}

# Mensajes Estructurados de Denegación
deny contains msg if {
    not valid_cloud_channel
    msg := "SEGURIDAD/LEGAL: Inferencia no enrutada por Vertex AI PSC, CMEK inferior a FIPS Nivel 3 o falta garantía de no entrenamiento."
}

deny contains msg if {
    not valid_input_structure
    msg := "OWASP LLM01/07: Prompt sin encapsulación XML, system_instruction no aislada o anomalía de inyección detectada."
}

deny contains msg if {
    not valid_data_privacy
    msg := "PRIVACIDAD: Carga útil con presencia de PII/PHI no ofuscada mediante tokenización reversible FPE."
}

deny contains msg if {
    not valid_output_contract
    msg := "OWASP LLM02: Salida sin validación de JSON Schema estricto o entorno de sandbox gVisor no verificado."
}

deny contains msg if {
    not valid_agency_governance
    msg := "OWASP LLM06: Operación de criticidad alta/financiera intentada sin autorización firmada HITL Ed25519."
}

deny contains msg if {
    not valid_cryptographic_audit
    msg := "FORENSE DIGITAL: Falta generación de manifiesto C2PA v2.1 o anclaje en el Árbol de Merkle RFC 6962."
}

deny contains msg if {
    not valid_finops_allocation
    msg := "FINANZAS: Falta imputación de tokens por centro de costos o canon de regalías IRC § 482 insuficiente."
}
