# <img src="assets/icons/hard-drive.svg" width="18" height="18" alt=""> Faire marcher le dashboard sans Cloudflare R2 (MinIO local)

Quand R2 n'est pas joignable depuis un poste (clés absentes, réseau, quota), le dashboard peut lire un **MinIO local** (le conteneur `urbanhub-minio` de `docker-compose.yml`, aussi appelé Silo). Il démarre vide : il faut lui copier le **Gold**, soit 19 objets pour 14 Mo environ.

## Étapes

1. **Exporter le Gold** depuis une machine qui joint R2 (lecture seule, utilise le `.env` de cette machine) :
   ```powershell
   uv run python scripts/gold_snapshot.py export --output data/gold-snapshot
   ```
   Zipper le dossier `data/gold-snapshot` et le transmettre au coéquipier (il n'est pas versionné).

2. **Démarrer MinIO** sur le poste concerné et déposer le dossier dans `data/gold-snapshot` :
   ```powershell
   docker compose up -d minio
   uv run python scripts/gold_snapshot.py import --input data/gold-snapshot
   ```
   Les trois buckets `urbanhub-bronze`, `urbanhub-silver` et `urbanhub-gold` existent déjà dans le MinIO du projet. Sur un MinIO tout neuf, ajouter `--create-bucket`. L'import refuse d'écrire sur R2 ou S3.

3. **Pointer le dashboard vers le MinIO local** : dans le `.env`, décommenter le bloc « Option A » (`MINIO_ENDPOINT=minio:9000`, `MINIO_ACCESS_KEY=minioadmin`, `MINIO_SECRET_KEY=minioadmin123`, `MINIO_SECURE=false`) et mettre en commentaire le bloc R2. Puis :
   ```powershell
   docker compose restart dashboard
   ```
   Le dashboard doit afficher `[OK] Data Lake connecté`.

## Ce qui marche et ce qui ne marche pas

- Les six onglets lisent uniquement le Gold : ils fonctionnent comme avec R2, avec les données de la date de l'export.
- Les données ne se mettent plus à jour : c'est une photo. Pour rafraîchir, refaire l'export puis l'import.
- Le tableau « Archives sur 5 ans » de l'onglet Historique lit le Bronze et le Silver : il indiquera « Non publiée » en local, puisqu'on n'y copie que le Gold.
- Les collecteurs (`--profile collect`) écrivent sur le lac configuré dans le `.env` ; ne pas les lancer en mode local sans savoir ce qu'on veut.

## Utile aussi pour les vidéos

Une photo locale du Gold donne un dashboard stable, indépendant du réseau et des quotas, pour enregistrer les démonstrations.
