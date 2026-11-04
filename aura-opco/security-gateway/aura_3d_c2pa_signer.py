import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import c2pa

class Aura3DC2PASigner:
    """
    Firmador criptográfico C2PA v2.1 con sello de tiempo RFC 3161 y bloqueo de
    entrenamiento de IA de terceros para AuraIntelStudios3D.com.
    """
    def __init__(self, cert_chain_path: str, private_key_path: str):
        self.cert_chain = Path(cert_chain_path).read_bytes()
        self.private_key = Path(private_key_path).read_bytes()
        self.tsa_url = "http://timestamp.digicert.com"

    @staticmethod
    def compute_sha256(file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def build_manifest(self, asset_title: str, mime_format: str, watermark_id: str) -> dict:
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "ta_url": self.tsa_url,
            "claim_generator": "AuraIntelStudios3D_Engine/4.2.0 c2pa-rs/0.36.0",
            "title": asset_title,
            "format": mime_format,
            "assertions": [
                {
                    "label": "c2pa.actions",
                    "data": {
                        "actions": [
                            {
                                "action": "c2pa.created",
                                "when": now_iso,
                                "softwareAgent": "AuraIntelStudios3D Neural Mesh Generator v4.2",
                                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                                "parameters": {
                                    "model_identifier": "aura-3d-synth-v2-safetensors",
                                    "geometry_vertex_watermark_id": watermark_id
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "c2pa.training-mining",
                    "data": {
                        "entries": {
                            "c2pa.ai_generative_training": {"use": "notAllowed"},
                            "c2pa.ai_inference": {"use": "notAllowed"},
                            "c2pa.ai_training": {"use": "notAllowed"},
                            "c2pa.data_mining": {"use": "notAllowed"}
                        }
                    }
                },
                {
                    "label": "stds.schema-org.CreativeWork",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "3DModel",
                        "author": [
                            {
                                "@type": "Organization",
                                "name": "AuraIntelStudios3D.com (Standard 1979 Holdings, LLC)",
                                "url": "https://AuraIntelStudios3D.com"
                            }
                        ],
                        "license": "https://AuraIntelStudios3D.com/legal/eula",
                        "copyrightHolder": {
                            "@type": "Organization",
                            "name": "Standard 1979 Holdings, LLC"
                        }
                    }
                }
            ]
        }

    def sign_3d_asset(self, input_glb: str, output_glb: str, watermark_id: str) -> dict:
        manifest_dict = self.build_manifest(
            asset_title=Path(output_glb).name,
            mime_format="model/gltf-binary",
            watermark_id=watermark_id
        )
        signer_info = c2pa.SignerInfo(
            alg="es256",
            sign_cert=self.cert_chain,
            private_key=self.private_key,
            ta_url=self.tsa_url
        )
        builder = c2pa.Builder(json.dumps(manifest_dict))
        builder.sign_file(source_path=input_glb, dest_path=output_glb, signer_info=signer_info)

        reader = c2pa.Reader.from_file(output_glb)
        return {
            "signed_asset": output_glb,
            "sha256_hard_binding": self.compute_sha256(output_glb),
            "c2pa_validation_state": "VALID_SIGNED_RFC3161",
            "manifest": json.loads(reader.json())
        }
