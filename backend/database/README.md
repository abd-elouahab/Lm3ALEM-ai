# Base de données — Connexion directe (sans inscription)

## Comptes clients pour se connecter directement

Mot de passe pour tous : **password123**

| Email | Nom |
|-------|-----|
| client1@test.com | Client Test |
| client2@test.com | Karima Essaidi |
| client3@test.com | Omar Tazi |
| client4@test.com | Fatima Bennani |
| client5@test.com | Samir Hassani |

## Comptes artisans (même mot de passe)

Exemples : **ahmed.zlayji@example.com**, **hassan.plombier@example.com** — tous les emails `*@example.com` du fichier `seed.sql` avec **password123**.

---

## Appliquer le seed (créer les clients dans la base)

### Option 1 : Script Python (recommandé si les tables existent déjà via l’app)

1. Démarrer l’app une fois pour créer les tables :  
   `uvicorn app.main:app --reload --port 8000`  
   Puis l’arrêter (Ctrl+C).

2. Depuis le dossier **backend** :
   ```bash
   python -m database.seed_db
   ```
   Cela crée les 5 clients. Pour les 20 artisans + 5 clients en une fois, utiliser l’option 2.

### Option 2 : Fichier SQL (PostgreSQL avec schema.sql déjà exécuté)

1. Créer les tables et les types si besoin :  
   `psql -U postgres -d lm3alem_ai -f database/schema.sql`

2. Insérer les données (nettoie les tables, réinitialise les séquences, insère 20 artisans + 5 clients) :  
   `psql -U postgres -d lm3alem_ai -f database/seed.sql`

Ensuite, sur le frontend : onglet **Connexion**, puis par exemple **client1@test.com** / **password123**.
