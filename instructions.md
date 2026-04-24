# Analyse du Projet "MadaTréso" : État Actuel et Fonctionnalités Manquantes

Suite à l'analyse de l'application (backend Django, frontend Next.js) et du document de vision (`new.md`), voici le bilan de ce qui a été réalisé et de ce qui manque pour atteindre le MVP.

## ✅ Ce qui est déjà implémenté (Acquis)

1. **Système de Rôles et d'Accès (Module PME partiel) :**
   - Rôles `MANAGER` et `ASSOCIER`.
   - Lien d'association (l'associé ajoute l'email du manager à l'inscription).
   - Validation des associés par le manager (avec niveau d'accès FULL/LIMITED).
   - Visibilité et gestion partagée des dépenses.
2. **Gestion des Dépenses (Transactions de base) :**
   - Création de dépenses (`Depense`) avec des articles (`DepenseItem`).
   - Système d'approbation des dépenses pour les accès limités (`PENDING`, `APPROVED`, `REJECTED`).
3. **Gestion Budgétaire simple :**
   - Création de budgets et suivi de l'historique (`Budget`, `BudgetHistory`).
   - Déduction automatique du budget lors de l'approbation d'une dépense.

## ❌ Ce qui manque par rapport au cahier des charges (À ajouter)

### 1. Consolidation Multi-sources (Comptes et Moyens de paiement)

- **Modèles de Comptes manquants :** Actuellement, tout est basé sur un "Budget" global. Il manque la distinction entre :
  - Comptes Bancaires (BNI, BMOI, etc.).
  - Comptes Mobile Money (MVola, Orange Money, Airtel Money).
  - Caisse (espèces / cash physique).
- **Import CSV :** Logique d'importation de relevés bancaires.

### 2. Fonctionnalités "Mobile Money" et Justificatifs

- **Smart Paste (Parsing SMS) :** Algorithme ou endpoint pour analyser le texte collé d'un SMS de confirmation (extraction du montant, référence, expéditeur).
- **Numérisation / OCR :**
  - Possibilité d'attacher une image/photo (champ `ImageField`) aux dépenses.
  - Intégration d'un outil d'OCR local ou d'une API pour extraire les données des reçus.

### 3. Catégorisation et Devises

- **Catégories de Dépenses :** Ajouter un champ/modèle "Catégorie" (Alimentation, Loyer, Jirama, Carburant, etc.) dans le modèle `Depense` ou `DepenseItem`.
- **Multi-devises :** Ajouter la gestion des devises (MGA par défaut, EUR, USD) dans les transactions et les comptes.

### 4. Budgétisation Avancée et Alertes

- **Alertes de seuil :** Implémenter un système de notification (Push ou Email) lorsque le budget ou le solde du compte atteint un niveau critique.

### 5. Exports Comptables (Module PME)

- **Endpoints d'Export :** Ajouter des fonctionnalités pour générer et télécharger des rapports au format Excel (CSV) ou PDF (structuré).

### 6. Optimisation Technique pour le "Offline-First"

- **Identifiants :** Remplacer les clés primaires `AutoField` (ID entiers) par des `UUID` pour faciliter la synchronisation offline-first depuis l'application mobile sans conflit d'IDs.
- **Horodatage de synchronisation :** Assurer que les champs `created_at` et `updated_at` puissent gérer des créations asynchrones datant d'avant la synchro.

### 7. Applications Clientes

- **Application Mobile Flutter :** Le frontend actuel est en React/Next.js (dossier `frontend`), ce qui est bon pour l'admin web, mais le cahier des charges exige expressément une app Flutter pour les performances sur mobile à Madagascar.

---

**Prochaines étapes recommandées :**

1. Mettre à jour les modèles de données (ajouter Catégories, Comptes Multi-sources, UUIDs).
2. Implémenter l'algorithme "Smart Paste" pour le Mobile Money.
3. Ajouter les fonctionnalités d'upload de justificatifs.
