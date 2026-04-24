# MeCode - API de Gestion de Budget et Dépenses

MeCode est une API REST construite avec Django REST Framework pour la gestion des budgets personnels et le suivi des dépenses. Elle permet également le partage de compte avec différents niveaux de permissions.

## Fonctionnalités Principales

### 1. Authentification
*   Système d'authentification basé sur **JWT (JSON Web Tokens)**.
*   Inscription des utilisateurs et gestion du profil.
*   Calcul automatique du budget total en temps réel.

### 2. Gestion du Budget
*   Ajout de plusieurs sources de budget (ex: Salaire, Freelance).
*   Suivi de l'historique des modifications du budget.
*   Calcul automatique du solde restant après chaque dépense.

### 3. Gestion des Dépenses
*   Création de dépenses contenant plusieurs articles (items).
*   Calcul automatique du montant total de la dépense à partir des prix des articles.
*   Validation du budget disponible avant l'enregistrement d'une dépense.

### 4. Partage de Compte et Collaborateurs
*   **Accès Complet (FULL)** : Un utilisateur autorisé peut voir et ajouter des dépenses qui sont validées immédiatement sur le compte du propriétaire.
*   **Accès Limité (LIMITED)** : Un utilisateur peut proposer des dépenses. Celles-ci restent en attente (`PENDING`) jusqu'à ce que le propriétaire les valide.
*   Les dépenses proposées n'affectent le budget du propriétaire qu'après confirmation.

---

## Documentation des Endpoints

### Authentification & Utilisateur
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/register/` | Créer un nouveau compte. |
| `POST` | `/api/login/` | Se connecter et obtenir les tokens JWT. |
| `POST` | `/api/token/refresh/` | Rafraîchir le token d'accès. |
| `GET` | `/api/me/` | Récupérer les infos de l'utilisateur. |

**Exemple `POST /api/register/` :**
```json
{
    "email": "manager@example.com",
    "password": "password123",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "MANAGER" // ou "ASSOCIER"
}
```
*Si `role` est `"ASSOCIER"`, ajoutez `"temp_manager_email": "manager@example.com"`.*

---

### Gestion des Budgets
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/budget/` | Lister les budgets. |
| `POST` | `/api/budget/` | Ajouter une source de budget. |
| `PUT` | `/api/budget/<id>/` | Modifier un budget. |

**Exemple `POST /api/budget/` :**
```json
{
    "titre": "Salaire Mensuel",
    "montant": 2500.00
}
```

---

### Gestion des Associés (Manager uniquement)
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/associates/` | Lister tous ses associés. |
| `POST` | `/api/associates/` | Créer directement un nouvel associé. |
| `GET` | `/api/associates/<id>/` | Voir le détail d'un associé. |
| `PATCH` | `/api/associates/<id>/` | Modifier un associé. |
| `DELETE` | `/api/associates/<id>/` | Supprimer/Détacher un associé. |
| `PATCH` | `/api/associates/<id>/approve/` | Approuver ou rejeter un associé spécifique. |

**Exemple `PATCH /api/associates/<id>/approve/` :**
```json
{
    "action": "APPROVE", // ou "REJECT"
    "access_level": "FULL" // ou "LIMITED"
}
```

**Exemple `POST /api/associates/` :**
```json
{
    "email": "associe@example.com",
    "password": "password123",
    "first_name": "Marc"
}
```

---

### Gestion des Dépenses
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/depense/` | Lister les dépenses. |
| `POST` | `/api/depense/` | Créer une dépense. |
| `PATCH` | `/api/depense/<id>/approve/` | Approuver une dépense en attente. |

**Exemple `POST /api/depense/` :**
```json
{
    "titre": "Courses Hebdo",
    "user": 1, // Optionnel: ID du propriétaire si compte partagé
    "items": [
        {"nom": "Pain", "prix": 1.50},
        {"nom": "Lait", "prix": 2.20}
    ]
}
```

**Exemple `PATCH /api/depense/<id>/approve/` :**
```json
{
    "action": "APPROVE" // ou "REJECT"
}
```

---

### Partage d'Accès Manuel
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/access/` | Lister les accès. |
| `POST` | `/api/access/` | Donner accès à son compte. |

**Exemple `POST /api/access/` :**
```json
{
    "shared_with": 3,
    "access_level": "LIMITED" // ou "FULL"
}
```

---

## Installation et Utilisation

1.  **Cloner le dépôt**
2.  **Installer les dépendances** : `pip install -r requirements.txt`
3.  **Migrations** : `python manage.py migrate`
4.  **Lancer le serveur** : `python manage.py runserver`

L'API est accessible par défaut sur `http://localhost:8000`.
