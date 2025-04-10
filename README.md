# Dashboard Admin - Gestion Parc Automobile

Une application Tkinter pour gérer un parc automobile avec des fonctionnalités CRUD.

## Prérequis

- Python 3.x
- MySQL Server
- phpMyAdmin

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Créez une base de données MySQL nommée `parc_automobile` via phpMyAdmin

4. Configurez la connexion à la base de données :
   - Ouvrez le fichier `dash_admin.py`
   - Modifiez les paramètres de connexion dans la méthode `__init__` :
     ```python
     self.conn = mysql.connector.connect(
         host="localhost",
         user="votre_utilisateur",
         password="votre_mot_de_passe",
         database="parc_automobile"
     )
     ```

## Utilisation

1. Lancez l'application :
```bash
python dash_admin.py
```

2. Fonctionnalités disponibles :
   - Ajouter une voiture
   - Modifier les informations d'une voiture
   - Supprimer une voiture
   - Changer l'état d'une voiture (disponible/indisponible)
   - Rechercher une voiture par marque, modèle ou immatriculation

## Structure de la base de données

La table `voitures` contient les champs suivants :
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- marque (VARCHAR(50))
- modele (VARCHAR(50))
- immatriculation (VARCHAR(20), UNIQUE)
- etat (VARCHAR(20), DEFAULT 'disponible')
- date_ajout (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP) 