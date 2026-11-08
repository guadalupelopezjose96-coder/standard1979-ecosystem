package standard1979.governance.gemini

import rego.v1

default allow := false

# 1. Validación de Canal Corporativo Autorizado
valid_endpoint if {
    input.request.endpoint_provider == "google_cloud_vertex_ai"
    input.request.private_service_connect == true
    input.request.customer_data_training_disabled == true
}

# 2. Endurecimiento de Entrada y Anti-Inyección (LLM01 / LLM07)
valid_prompt_structure if {
    input.request.system_instruction_isolated == true
    input.request.user_input_xml_encapsulated == true
    count(detected_injection_patterns) == 0
}

detected_injection_patterns contains pattern if {
    some pattern in input.security.detected_anomalies
    blocked := {"PROMPT_INJECTION_DIRECT", "SYSTEM_PROMPT_EXTRACTION_ATTEMPT", "JAILBREAK_EVASION"}
    blocked[pattern]
}

# 3. Privacidad y Ofuscación de Datos (DLP)
valid_privacy_compliance if {
    input.security.dlp_scan_completed == true
    input.security.unredacted_pii_count == 0
}

# 4. Manejo Seguro de Salida y Tipado Estricto (LLM02)
valid_output_contract if {
    input.request.enforce_json_schema == true
    input.request.response_schema_defined == true
}

# 5. Puerta Human-in-the-Loop en Function Calling (LLM06)
valid_agency_control if {
    input.operation.criticality == "HIGH"
    input.operation.hitl_human_signature_valid == true
}

valid_agency_control if {
    input.operation.criticality != "HIGH"
}

# 6. Registro Forense Criptográfico (Fed. R. Evid. 902 / C2PA)
valid_cryptographic_audit if {
    input.audit.merkle_leaf_computed == true
    input.audit.c2pa_manifest_staged == true
}

# Autorización Global
allow if {
    valid_endpoint
    valid_prompt_structure
    valid_privacy_compliance
    valid_output_contract
    valid_agency_control
    valid_cryptographic_audit
}

# Notificaciones Formales de Denegación
deny contains msg if {
    not valid_endpoint
    msg := "SEGURIDAD/LEGAL: El endpoint no es Vertex AI privado o carece de la garantía de exclusión de reentrenamiento."
}

deny contains msg if {
    not valid_prompt_structure
    msg := "OWASP LLM01/07: El prompt carece de encapsulación XML estructurada o disparó banderas de inyección/extracción."
}

deny contains msg if {
    not valid_privacy_compliance
    msg := "PRIVACIDAD: Carga útil contiene datos PII/PHI no ofuscados por la pasarela DLP."
}

deny contains msg if {
    not valid_output_contract
    msg := "OWASP LLM02: Solicitud sin forzado de JSON Schema cerrado para garantizar tipado estricto."
}

deny contains msg if {
    not valid_agency_control
    msg := "OWASP LLM06: Acción de alta criticidad intentada sin firma criptográfica HITL requerida."
}

deny contains msg if {
    not valid_cryptographic_audit
    msg := "FORENSE DIGITAL: No se computó el nodo para el Árbol de Merkle RFC 6962 o falta el manifiesto C2PA."
}
