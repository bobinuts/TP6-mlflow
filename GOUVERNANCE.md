# GOUVERNANCE — Séance 6, partie 2

Théo Pellicano · M2 IA & Data · YNOV Campus Montpellier · 20/11/2026

Le classement AI Act est mon analyse de cours, pas un avis juridique. Il s'appuie sur le règlement (UE) 2024/1689 et, pour ISIC, sur le règlement (UE) 2017/745 (dispositifs médicaux, « MDR »).

## 2.1 — Classer selon l'AI Act

| Sujet | Usage du service | Niveau proposé | Article ou annexe invoqué | Ce qui ferait changer de niveau |
|---|---|---|---|---|
| **ISIC approfondi** | Trier des lésions cutanées pour qu'un praticien décide lesquelles examiner (rappel visé 0,95), à partir du tabulaire, des vignettes ou des deux | **2 — haut risque**, dès que le service est destiné à un usage médical | Art. 6, § 1 et annexe I, section A : le logiciel est un dispositif médical (règlement 2017/745) ; une aide au diagnostic relève au moins de la classe IIa (règle 11), donc d'une évaluation par organisme notifié. Exigences des art. 9 à 15 (risques, données, traçabilité, supervision humaine). | Un usage de recherche ou de pédagogie sur un jeu public, sans mise en service auprès de patients ni finalité médicale déclarée : hors dispositif médical, donc niveau 4 (et exclusion de la recherche scientifique, art. 2, § 6). Aucun passage vers le niveau 1 ou 3 : pas de pratique interdite, pas de contenu synthétique. |
| **DEEP-VOICE** | Dire si un extrait audio est une voix réelle ou une voix convertie (huit personnalités) | **4 — minimal** pour un détecteur générique | Aucun article d'obligation propre : un classifieur de « réel ou converti » n'identifie personne. L'art. 50 vise celui qui *produit* des contenus synthétiques (§ 2) ou les diffuse (§ 4), pas le détecteur. | **Niveau 3** si le service produit ou convertit des voix (art. 50 : marquage, information). **Niveau 2** s'il sert à identifier un locuteur à distance (annexe III, point 1) ou à évaluer la fiabilité d'une preuve pour la police ou la justice (annexe III, point 6). **Niveau 1** s'il déduit des émotions au travail ou à l'école (art. 5, § 1, f). |
| **Eedi** | Pour une mauvaise réponse à une question à choix multiple, proposer les idées fausses les plus probables d'un catalogue | **2 — haut risque probable**, si le résultat touche un élève | Annexe III, point 3, b : systèmes destinés à évaluer les acquis, y compris pour orienter l'apprentissage. L'art. 6, § 3 permet d'en sortir pour une tâche préparatoire étroite, sauf profilage de personnes. | Un outil réservé aux concepteurs de questions, qui travaille sur des réponses agrégées sans désigner un élève : **niveau 4**. À l'inverse, un usage qui note, oriente ou admet un élève reste au niveau 2 ; la détection d'émotions des élèves serait au **niveau 1**. |

Le calendrier ne change pas le classement : depuis l'omnibus numérique publié au Journal officiel le 24 juillet 2026, les obligations des systèmes de l'annexe III s'appliquent à partir du 2 décembre 2027 et celles des systèmes de l'annexe I (dont les dispositifs médicaux) à partir du 2 août 2028.

### Question 2.1 — Classement du sujet ISIC approfondi

1. **Niveau retenu : 2, haut risque**, pour DermaScan présenté comme outil de tri destiné à des dermatologues.
2. **Raison :** un logiciel qui aide à décider d'examiner une lésion est un dispositif médical au sens du règlement 2017/745 ; sa règle 11 le place au moins en classe IIa, donc sous évaluation par un organisme notifié.
3. L'art. 6, § 1 de l'AI Act et l'annexe I (section A) en font alors un système à haut risque ; les niveaux 1 et 3 ne s'appliquent pas (aucune pratique interdite, aucun contenu synthétique, aucune conversation avec une machine).
4. **L'usage précis qui le ferait changer :** le même modèle servi seulement pour la recherche ou l'enseignement, sur un jeu public, sans mise en service ni finalité médicale déclarée, tomberait au niveau 4.
5. Le niveau 2 pèse déjà sur mes choix : rappel fixé avant mesure, version promue et validée, traçabilité jusqu'aux données, supervision humaine de la décision `a_examiner`.

## 2.2 — Ce que je n'ai pas le droit de journaliser

Ligne de journal de S3 (`JOURNALISATION_INFERENCES.md`, partie 6.2), telle que l'API de S5 l'écrit. Les durées reprennent la partie 6.3 de S3, sauf une, signalée sous le tableau.

| Champ | Conservé ? | Transformation | Durée de conservation | Besoin nommé qui la justifie |
|---|---|---|---|---|
| `ts` | Oui | UTC, milliseconde, suffixe `Z` | 12 mois | Ordonner les événements d'une réclamation ou d'un incident ; sans lui aucune reconstitution. |
| `request_id` | Oui | UUID v4, généré par le service si l'appelant n'en fournit pas de valide | 12 mois | Relier une réclamation à une ligne ; aléatoire, il n'identifie personne. |
| `model_version` | Oui | Lu dans le paquet servi, jamais dans une variable d'environnement | 12 mois, et tant que la version reste au registre | Répondre à « quel modèle a produit cette réponse », première question d'un audit ; c'est le premier maillon vers le run. |
| `image_digest` | Oui | Digest `sha256:…` de l'image conteneur, injecté au déploiement | 12 mois, et tant que l'image reste au registre | Désigner un contenu immuable pour rejouer la décision ; un tag est mutable. |
| `patient_ref` | Oui, **jamais l'identifiant en clair** | `sha256(sel:patient_id)[:16]`, sel `INFERENCE_LOG_SALT` tenu hors du journal et du dépôt | 12 mois ; le sel est détruit à l'échéance | Relier les lésions d'un même patient pour la charge d'alertes et le suivi, sans pouvoir remonter au patient sans le sel. |
| `probabilite_maligne` | Oui | 6 décimales | 12 mois | Rejouer la décision au seuil appliqué et suivre la dérive de la sortie (S5). |
| `decision` | Oui | `a_examiner` / `surveillance` (S4, S5) ou `non_signale` (S2, S3), valeur brute | 12 mois | C'est l'objet même d'une réclamation. |
| `covariables` | Oui, **réduites** | Âge en tranche de 10 ans, sexe, site anatomique, `tbp_tile_type` ; aucune mesure `tbp_lv_*`, ni âge exact, ni `isic_id` | **90 jours** pour les valeurs ligne à ligne ; leurs distributions agrégées (PSI) : 13 mois | Mesurer la dérive des entrées (S5). Les agrégats suffisent à ce besoin. L'audit d'une décision ne les exige pas : il rejoue la décision avec la charge que le praticien peut soumettre à nouveau. |

**Écart avec S3 : la durée des covariables passe de 12 mois à 90 jours.** Le besoin de la dérive se satisfait avec des agrégats. Garder 12 mois les valeurs ligne à ligne, croisées avec `patient_ref` et l'horodatage, conserve un quasi-identifiant sans besoin qui le justifie.

Ne figurent pas dans la ligne, et ne doivent jamais y figurer : la charge utile, la vignette, ses pixels ou tout vecteur dérivé de l'image, `isic_id`, `patient_id`, l'adresse IP, un jeton, le sel.

### Question 2.2 — Une vignette de peau peut-elle être pseudonymisée par hachage ?

Non. Le hachage remplace un identifiant par une empreinte, mais ne transforme pas le contenu : l'image reste l'image, donnée de santé (art. 9 du RGPD) qui peut reconnaître un tatouage, une cicatrice ou un grain de beauté. Une empreinte du fichier ne protège pas non plus, car quiconque détient la vignette retrouve la ligne en recalculant l'empreinte : c'est un pseudonyme, donc encore une donnée personnelle (considérant 26).
Cela interdit de journaliser la vignette, ses pixels, une miniature, un vecteur d'attributs qui en est tiré, ainsi que `isic_id` qui permet de la retrouver ; ce que le journal garde de l'image tient dans la sortie du modèle et dans `request_id`.

### Question 2.3 — Le jour où le service reçoit des données réelles

1. Le journal cesse d'être celui d'un jeu public : chaque ligne `patient_ref` + covariables + horodatage devient un enregistrement de données de santé (art. 9 du RGPD). Il faut alors une base légale et une condition de l'art. 9, § 2 (soins, ou consentement), une analyse d'impact (art. 35), une inscription au registre des traitements et un hébergement dans l'Union (`germanywestcentral` convient).
2. Les durées de 12 mois et de 90 jours deviennent des engagements à valider avec un délégué à la protection des données ; le sel passe dans un coffre (Key Vault) et la rotation à l'échéance sert d'effacement ; la purge se configure sur la plateforme, pas seulement dans le code.
3. La k-anonymité des covariables se mesure par centre (petits centres, quasi-identifiants) ; il faut pouvoir retrouver et effacer toutes les lignes d'un patient à sa demande (art. 15 et 17), et le niveau 2 de l'AI Act ajoute la conservation automatique des journaux d'un système à haut risque (art. 12 et 19).

## 2.3 — Une ligne de journal mène au commit

| Maillon | Identifiant qui mène au suivant | Où il est écrit | Présent aujourd'hui ? |
|---|---|---|---|
| Ligne de journal | `image_digest` et `model_version` | Ligne JSON de l'API (S3 en spécification, S5 en production : `journal_azure.jsonl`) | Oui pour `model_version` ; `image_digest` est `null` si le réglage `IMAGE_DIGEST` n'est pas injecté (valeur `null` dans `journal_local.jsonl` de S5). |
| Image | `sha256_fichier_servi` (fichier modèle dans l'image) | `/model/info` de l'API et registre ACR (digest de l'image) | Oui pour l'API de S5 : elle expose l'empreinte du fichier servi. Elle ne peut pas encore la comparer au registre de modèles, qui n'existe que depuis aujourd'hui. |
| Version de modèle au registre | `run_id` et tag `sha256_modele` | Registre MLflow du poste (`suivi/mlflow.db`) | Oui pour `dermascan-tabulaire` après la promotion (1.5). Non pour les modèles de S4 et S5 (ResNet18) : ils n'ont jamais été enregistrés. |
| Run | tag `sha256_manifeste`, graine, hyperparamètres | Run MLflow (tags et paramètres) | Oui, pour les quatre runs de la partie 1. |
| Manifeste de données | `sha256` de la source, `commit` | `donnees/manifeste.json` | Oui pour les empreintes et les effectifs ; **non pour le commit** (`hors-git`). |
| Commit du code | hash Git | Historique Git du dépôt | **Non** : le dossier n'est pas un dépôt Git au moment où `preparer.py` écrit le manifeste. |

### Question 2.4 — `commit : hors-git`

Le dernier maillon est rompu : le manifeste porte la valeur `hors-git`, donc rien ne permet de dire quelle version du code a produit les données ni, par le run, le modèle. Le geste de la partie 3 qui le répare est `git init` puis le premier commit, avant tout code : `preparer.py` lance alors `git rev-parse` et écrit un vrai hash dans le manifeste.
Le script ne vérifie pas que l'arbre de travail est propre : un code modifié mais non validé porterait quand même le hash du dernier commit. Il faut donc valider avant de lancer.

### Question 2.5 — `1.0.0` contre `dermascan-tabulaire v2`

Il faut un seul identifiant, écrit à la promotion : `promouvoir.py` inscrit la version du registre (`dermascan-tabulaire@v2`), le `run_id` et `sha256_modele` dans `modele_meta.json`, dans le paquet qui part en image. L'API lit `model_version` dans ce paquet (règle de S3) : la ligne de journal porte alors `dermascan-tabulaire@v2`, et la jointure avec le registre devient une égalité de chaînes.
Le test `verifier_chaine.py` compare ensuite cette valeur à celle de l'alias `production` et échoue si elles divergent ; le numéro SemVer peut rester comme étiquette du registre, jamais comme second identifiant.

## Sources consultées le 20/11/2026

- Omnibus numérique sur l'IA, nouvelles échéances (2 décembre 2027 et 2 août 2028), publié au JOUE le 24 juillet 2026 : <https://fpf.org/?p=250371>
- Dispositifs médicaux et haut risque (art. 6, § 1, annexe I, organisme notifié) : <https://www.taylorwessing.com/en/international-life-sciences-newsletter/life-sciences-legal-lens-vol-2/update-ai-enabled-medical-devices-and-ivds-confirmed-as-high-risk>
