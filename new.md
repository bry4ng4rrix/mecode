# PROMPT COMPLET — Application "MadaTréso" (Gestion de Trésorerie Madagascar)

## 1. VISION ET MARCHÉ CIBLE

Développer une solution de gestion de trésorerie unifiée pour **Madagascar**, ciblant les particuliers, les entrepreneurs individuels et les PME. L'objectif est de consolider en un seul point : les banques locales, le cash et surtout le **Mobile Money** (MVola, Orange Money, Airtel Money).

- **Localisation :** Madagascar (Conformité CSBF et RGPD).
- **Langues :** Français (Admin/Pro) et Malagasy (Interface utilisateur/standard).
- **Devise :** Ariary (MGA) par défaut, avec gestion multi-devises (EUR/USD) pour l'export.

## 2. FONCTIONNALITÉS MÉTIER (MVP PRIORITAIRE)

### 2.1 Consolidation Multi-sources

- **Comptes Bancaires :** Saisie manuelle assistée ou import CSV (BNI, BMOI, Société Générale, BOA, etc.).
- **Mobile Money (L'alternative au SMS) :** \* _Smart Paste :_ Champ de saisie intelligent permettant à l'utilisateur de coller le texte d'un SMS de confirmation reçu. L'application extrait automatiquement le montant, la référence et l'expéditeur via un script de parsing local.
  - _Capture de preuve :_ Capture d'écran de la transaction avec **OCR local** pour valider les données.
- **Gestion de Caisse :** Tenue de brouillard de caisse pour le cash physique.

### 2.2 Transactions et Justificatifs

- **Enregistrement Express :** Workflow en 3 clics pour les dépenses courantes.
- **Numérisation de Reçus :** OCR optimisé pour les factures thermiques et reçus manuscrits (courants à Madagascar).
- **Catégorisation simplifiée :** Alimentation, Loyer, Jirama, Carburant, Frais de scolarité, etc.

### 2.3 Budgétisation et Alertes

- **Suivi de consommation :** Barre de progression visuelle simple par catégorie.
- **Alertes de seuil :** Notifications push (ou email) avant d'atteindre le solde critique.

### 2.4 Module PME (Optionnel mais structuré)

- **Multi-accès :** Propriétaire (vue globale) et Gérant/Caissier (saisie uniquement).
- **Exports Comptables :** Format compatible avec les logiciels utilisés localement (Excel/PDF structuré).

## 3. ARCHITECTURE TECHNIQUE ET PERFORMANCES

### 3.1 Stack Frontend (Le choix de l'efficacité)

- **Mobile :** **Flutter** (impératif). Offre les meilleures performances sur les smartphones d'entrée de gamme (type Itel, Tecno, Samsung série A) très présents sur le marché malgache.
- **Web :** React avec Vite (léger et rapide).

### 3.2 Backend et Données

- **Langage :** Node.js (NestJS) ou Go pour la légèreté.
- **Base de données :** PostgreSQL.
- **Stratégie Offline :** **Offline-first obligatoire**. Les données doivent pouvoir être saisies sans réseau et synchronisées dès que la 4G/LTE ou le Wi-Fi est stable. Utilisation de _SQLite_ ou _Isar_ en local.

### 3.3 Sécurité

- Chiffrement des données financières au repos.
- Authentification biométrique simple (Empreinte digitale).

## 4. DESIGN ET UX (PRINCIPES LOCAUX)

- **Légèreté du Bundle :** L'application ne doit pas dépasser **30 Mo** (coût des données mobiles important).
- **Mode Sombre :** Pour économiser la batterie.
- **UI Épurée :** Icônes explicites pour pallier les barrières linguistiques.

## 5. ROADMAP DE DÉVELOPPEMENT

- **Mois 1 :** Socle technique, gestion du cash et système "Smart Paste" pour Mobile Money.
- **Mois 2 :** Module de scan de reçus (OCR) et gestion budgétaire.
- **Mois 3 :** Rapports PDF/Excel et synchronisation multi-appareils.
- **Mois 4 :** Bêta-test avec un panel de 50 PME à Antananarivo.

## 6. INSTRUCTIONS POUR L'IA DE DÉVELOPPEMENT

1.  Générer le schéma de base de données PostgreSQL incluant l'isolation par utilisateur.
2.  Écrire l'algorithme de "Smart Paste" capable de parser les formats de messages MVola/Orange Money/Airtel Money sans accès direct aux SMS système.
3.  Proposer une structure de projet Flutter optimisée pour le mode hors-ligne.
4.  Établir une liste d'endpoints API REST documentés sous Swagger.

> **Note de rigueur :** Ne pas implémenter de fonctionnalités de lecture automatique de SMS système pour garantir la compatibilité iOS et la conformité aux stores d'applications.
