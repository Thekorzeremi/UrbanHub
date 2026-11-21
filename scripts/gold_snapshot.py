#!/usr/bin/env python3
"""Copie du Gold du Data Lake vers un MinIO local : le dashboard marche alors sans Cloudflare R2.

Le Gold fait environ 14 Mo (les 15 tables lues par le dashboard). Deux étapes :

1. Export, sur une machine qui joint R2 (lit le .env, ne fait que lire) :
       python scripts/gold_snapshot.py export --output data/gold-snapshot

   Le dossier produit peut être zippé et transmis à un coéquipier qui ne joint pas R2.

2. Import dans le MinIO local (conteneur `urbanhub-minio`, `docker compose up -d minio`) :
       python scripts/gold_snapshot.py import --input data/gold-snapshot

Ensuite, dans le .env, pointer le dashboard vers le MinIO local (bloc « Option A » de .env.example :
MINIO_ENDPOINT=minio:9000, minioadmin, minioadmin123, MINIO_SECURE=false), puis `docker compose restart dashboard`.

Sécurité : l'import refuse d'écrire sur Cloudflare R2 et ne crée aucun bucket sans `--create-bucket`
(MinIO local uniquement).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_BUCKET = "urbanhub-gold"


def export_gold(output: Path) -> int:
    try:
        from citybikes_stream import build_minio_client
    except ImportError:
        from scripts.citybikes_stream import build_minio_client
    client, buckets = build_minio_client()
    bucket = buckets["gold"]
    output.mkdir(parents=True, exist_ok=True)
    manifest = []
    for obj in client.list_objects(bucket, recursive=True):
        destination = output / obj.object_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        client.fget_object(bucket, obj.object_name, str(destination))
        manifest.append({"key": obj.object_name, "size": obj.size})
        print(f"Exporté : {obj.object_name} ({obj.size / 1e6:.2f} Mo)")
    (output / "manifest.json").write_text(json.dumps({"bucket": bucket, "objects": manifest}, indent=2), encoding="utf-8")
    print(f"{len(manifest)} objets, {sum(m['size'] for m in manifest) / 1e6:.1f} Mo -> {output}")
    return len(manifest)


def import_gold(source: Path, endpoint: str, access_key: str, secret_key: str, bucket: str, create_bucket: bool) -> int:
    from minio import Minio

    if "cloudflarestorage.com" in endpoint or "amazonaws.com" in endpoint:
        raise SystemExit("Import refusé : cette commande ne doit écrire que dans un MinIO local, jamais sur R2 ou S3.")
    manifest_path = source / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"{manifest_path} introuvable : lancer d'abord l'export.")
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)
    if not client.bucket_exists(bucket):
        if not create_bucket:
            raise SystemExit(f"Bucket {bucket} introuvable sur {endpoint}. Le créer avec --create-bucket (MinIO local uniquement).")
        client.make_bucket(bucket)
        print(f"Bucket créé : {bucket}")
    sent = 0
    for item in json.loads(manifest_path.read_text(encoding="utf-8"))["objects"]:
        client.fput_object(bucket, item["key"], str(source / item["key"]), content_type="application/octet-stream")
        sent += 1
        print(f"Importé : {bucket}/{item['key']}")
    print(f"{sent} objets importés dans {bucket} sur {endpoint}")
    return sent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    exp = sub.add_parser("export", help="télécharge le bucket Gold configuré dans le .env (lecture seule)")
    exp.add_argument("--output", type=Path, default=Path("data/gold-snapshot"))
    imp = sub.add_parser("import", help="envoie le dossier exporté dans un MinIO local")
    imp.add_argument("--input", type=Path, default=Path("data/gold-snapshot"))
    imp.add_argument("--endpoint", default="localhost:9000", help="MinIO local vu depuis votre poste (défaut localhost:9000)")
    imp.add_argument("--access-key", default="minioadmin")
    imp.add_argument("--secret-key", default="minioadmin123")
    imp.add_argument("--bucket", default=DEFAULT_BUCKET)
    imp.add_argument("--create-bucket", action="store_true", help="crée le bucket s'il n'existe pas (MinIO local)")
    args = parser.parse_args(argv)
    if args.command == "export":
        export_gold(args.output)
    else:
        import_gold(args.input, args.endpoint, args.access_key, args.secret_key, args.bucket, args.create_bucket)
    return 0


if __name__ == "__main__":
    sys.exit(main())
