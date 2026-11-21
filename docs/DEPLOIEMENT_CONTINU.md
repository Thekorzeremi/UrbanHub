# <img src="assets/icons/rocket.svg" width="18" height="18" alt=""> Faire tourner la collecte en continu

Objectif : des données toujours fraîches dans le Data Lake, sans que quelqu'un relance un script à la main. Les trois flux ont un service Docker dédié, dans un profil `collect` qui n'est **pas** démarré par un simple `docker compose up`.

## <img src="assets/icons/package.svg" width="18" height="18" alt=""> Les trois services

| Service | Commande exécutée | Cadence | Ce qu'il met à jour |
| :--- | :--- | :--- | :--- |
| `collector-citybikes` | `scripts/citybikes_stream.py --interval-seconds 300` | toutes les 5 minutes | Bronze, Silver et Gold mobilité (Gold recalculé depuis le Silver publié dans R2) |
| `collector-openaq` | `python -m src.openaq_pipeline` | toutes les 2 heures, fenêtre relue de 12 h | Bronze, Silver, `pollution_hourly` et `city_hourly` |
| `collector-weather` | `scripts/openmeteo_batch.py --upload` | toutes les heures | `weather_hourly` et `weather_daily` |

Démarrer, suivre et arrêter :

```powershell
docker compose --profile collect up -d --build
```
```powershell
docker compose --profile collect ps
```
```powershell
docker compose logs -f collector-citybikes
```
```powershell
docker compose --profile collect stop
```

Les services lisent le fichier `.env` (clés R2). Ne pas y fixer `MINIO_ENDPOINT` vers `minio:9000` : les données iraient dans le MinIO local au lieu de R2. Le dashboard affiche la **fraîcheur** de chaque source : si une ligne passe en « En retard », le service correspondant s'est arrêté.

## <img src="assets/icons/building.svg" width="18" height="18" alt=""> Où les faire tourner

| Option | Avantages | Limites |
| :--- | :--- | :--- |
| **Un PC ou un serveur toujours allumé avec Docker** (recommandé) | Rien à créer, `restart: unless-stopped` relance les services après un redémarrage de Docker | Désactiver la mise en veille ; Docker Desktop doit démarrer avec Windows ; la collecte s'arrête si le PC s'éteint |
| **Une machine virtuelle Linux avec Docker** (offre gratuite ou crédits étudiants, à vérifier sur votre compte) | Indépendante du PC d'un membre, disponible 24 h sur 24 | Création de compte et mise en place à prévoir |
| **Tâche planifiée GitHub Actions** (non testée ici) | Aucune machine à garder allumée | Cadence minimale de 5 minutes, souvent retardée ; les clés R2 doivent être mises en secrets du dépôt ; le décompte de minutes dépend de l'offre du dépôt |

Quelle que soit l'option, **une seule machine** fait tourner la collecte vers R2 (voir ci-dessous).

## <img src="assets/icons/alert.svg" width="18" height="18" alt=""> Quota de l'API CityBikes : ce qu'on fait et ce qu'on ne fait pas

Le 19/11/2026, l'API a répondu `HTTP 429` avec un délai d'attente d'environ 40 minutes, après plusieurs appels de test depuis la même adresse. Le quota est un garde-fou du service : on le **respecte**, on ne le contourne pas (pas de rotation d'adresses ni de changement d'identité du client, qui violent l'esprit de la limite et peuvent faire bloquer toute l'équipe).

Ce que fait le script :
- au premier `429`, il **n'interroge plus aucun réseau** jusqu'à la fin de l'attente indiquée par l'API (`Retry-After`), au lieu de réessayer à chaque cycle ;
- il n'écrit rien tant qu'il est en pause, et ne touche pas au Gold publié ;
- il fait 3 appels par cycle (un par ville), soit 36 appels par heure, avec 1 seconde entre les villes.

Ce que l'équipe doit faire :
- **une seule machine** collecte vers R2 (les collecteurs de plusieurs membres s'additionnent sur la même adresse et dépassent le quota) ;
- ne pas lancer de tests qui appellent l'API en direct : utiliser `--storage local` pour un test, ou les tests avec faux stockage ;
- si le débit autorisé reste trop faible, contacter CityBikes plutôt que multiplier les clients.

## <img src="assets/icons/hard-drive.svg" width="18" height="18" alt=""> Volume de stockage à prévoir

| Flux | Volume estimé | Remarque |
| :--- | :--- | :--- |
| CityBikes Bronze | environ 1 Mo par cycle, soit environ 290 Mo par jour | Les réponses brutes sont volumineuses (Paris : 0,7 Mo) |
| CityBikes Silver et Gold | environ 60 Mo par jour | Parquet compressé |
| OpenAQ | quelques Mo par jour avec la fenêtre de 12 h | `clean_and_transform_to_silver` relit tout le Bronze à chaque exécution : le temps de calcul grandit avec le nombre d'objets |
| Météo | négligeable | Les fichiers sont réécrits, pas accumulés |

Le quota gratuit de R2 est de 10 Go : à ce rythme, environ 3 semaines de collecte CityBikes. Prévoir d'arrêter la collecte après l'enregistrement des vidéos, ou de purger les anciens Bronze CityBikes une fois le Silver validé. Aujourd'hui le lac occupe environ 0,15 Go.

## <img src="assets/icons/check-circle.svg" width="18" height="18" alt=""> Vérifier que tout tourne

1. Le dashboard ([http://localhost:8866](http://localhost:8866)) affiche une ligne « À jour » pour la météo, la mobilité et la pollution.
2. `docker compose --profile collect ps` montre les trois services en état `Up`.
3. Après quelques heures, relancer `notebooks/04_analyses_mobilite.ipynb` : le nombre d'heures observées augmente et les messages `[ATTENTION]` disparaissent section par section.

## <img src="assets/icons/alert.svg" width="18" height="18" alt=""> Point d'attention : le code des collecteurs est celui de votre dossier

Les services Docker montent le dossier du projet (`.:/app`). Le collecteur exécute donc **le code de la branche actuellement extraite sur la machine qui le fait tourner**. Changer de branche, ou se placer sur une branche en retard, fait exécuter l'ancien code au cycle suivant : le 21/11/2026, la pollution est restée figée à la veille parce que le collecteur OpenAQ a tourné avec une version d'avant le correctif de pagination, alors que l'API avait des données plus récentes.

- Sur la machine de collecte, rester sur `main` à jour (`git pull --rebase`) et ne pas y développer.
- Après un changement de branche ou un `git pull`, relancer les collecteurs : `docker compose --profile collect restart`.
- Pour vérifier la fraîcheur : le tableau du dashboard, ou `docker compose logs --tail 40 collector-openaq` (le message « Silver incrémental » indique le code à jour).
