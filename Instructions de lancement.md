1\. Prérequis



* Docker et Docker compose
* Node.js
* Python 3.12
* Navigateur



2\. Installation et lancement



1. Ouvrir le terminal à la racine du projet
2. Lancer la base de donnée dockerisée avec "docker-compose up -d"
3. Vérifier que MySQL tourne sur le port 3306 par défaut, ou un autre si déjà occupé
4. Créer un environnement virtuel si votre IDE ne le fait pas par défaut
5. Installer les dépendances rapidement avec "pip install -r requirements.txt
6. Vérifier que les informations de la DB dockerisée correspondent au champs de la connexion dans le main.py
7. A la racine, faire un npm install et dans le sous dossier frontend, en faire un autre (2 package.json).
8. A la racine, lancer le projet avec "npm run dev". Le frontend et le backend devrait se lancer en même temps grâce à concurrently
9. Le frontend devrait être disponible sur http://localhost:5173



3\. Utilisation de la solution et fonctionnalités



Ouvrir le navigateur sur http://localhost:5173



* Créer un compte ou se connecter avec un compte existant.
* Aller dans projet (Navbar) et créer un projet : cliquer sur “+ Nouveau projet”, remplir les champs et sauvegarder.
* Accéder au Kanban avec un click et créer des tâches au sein d’un projet et assigner des utilisateurs.
* Modifier ou supprimer un projet (bouton "Modifier") ou une tâche (Mécanique de double click) si vous en êtes le propriétaire ou un utilisateur assigné.
* Tableau Kanban : faire glisser les tâches entre colonnes (statuts) pour suivre l’avancement.
* Partager le projet : utiliser l’option “Ajouter un utilisateur au projet” pour donner accès à d’autres utilisateurs.





