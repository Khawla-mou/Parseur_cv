# Étape 1 : Utiliser une image Python officielle et légère
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 2 : Copier le fichier de dépendances et les installer
# Cette étape est séparée pour bénéficier du cache de Docker.
# Si vos dépendances ne changent pas, cette couche ne sera pas reconstruite.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 3 : Copier le reste du code de l'application
COPY . .

# Étape 4 : Exposer le port sur lequel l'application va écouter
EXPOSE 5000

# Étape 5 : Définir la commande pour lancer l'application
# --host=0.0.0.0 est CRUCIAL pour que l'application soit accessible
# depuis l'extérieur du conteneur.
# On active le mode debug pour le développement.
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--debug"]