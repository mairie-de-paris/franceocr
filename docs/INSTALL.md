# Installation

## Docker
Une image docker prête à l'emploi est disponible sur [Docker Hub]().
Une fois docker et docker-compose installés, il suffit de lancer le serveur avec la commande `docker-compose up -d`.
Le service est alors disponible à l'adresse `http://localhost:5000`. Il est recommandé de le placer devant un reverse proxy HTTPS.

## Système
Si docker n'est pas utilisable, il est possible d'installer les dépendances sur le système hôte.
Suivant le système, il peut être nécessaire de les compiler depuis les sources (obligatoire pour Tesseract 4).

### Dépendances
- python>=3.5
- numpy>=1.10
- opencv>=3
- [tesseract>=4](https://github.com/tesseract-ocr/tesseract/wiki/Compiling)

Toutes les dépendances python stipulées dans le fichier `requirements.txt`.
Il est conseillé des les installer avec `pip install -r requirements.txt`.

### Lancement
Il est recommandé d'utiliser un serveur WSGI pour executer le serveur. Nous recommandons gunicorn.
La commande de base, ajustable selon les besoins, est `gunicorn --config api/gunicorn.conf --log-config api/logging.conf -b :8000 --chdir api server:server`.
