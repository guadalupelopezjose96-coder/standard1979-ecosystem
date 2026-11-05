# GUÍA TÉCNICA: PRIVACYINFO.XCPRIVACY EN ECOSISTEMAS APPLE

1. UBICACIÓN: Colocar en la raíz del framework `Standard1979Kit` o paquete Swift Package Manager (SPM).
2. TRACKING: Declarado en `false`. Exime a la app de requerir el diálogo invasivo de `AppTrackingTransparency` (ATT).
3. EXPORTACIÓN DE REPORTE: En Xcode, usar `Product > Generate Privacy Report` para validar que no existan discrepancias antes de enviar la compilación a App Store Connect.
4. AUDITORÍAS PERIÓDICAS: Toda adición de dependencias Cocoapods/SPM de terceros debe auditarse para confirmar que incluya su respectivo `PrivacyInfo.xcprivacy`.
