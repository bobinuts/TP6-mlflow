# MESURES — Séance 6, partie 1 (suivre : runs et registre)

Théo Pellicano · M2 IA & Data · YNOV Campus Montpellier · 20/11/2026

**Poste :** Windows 11, PowerShell 5.1, Python 3.12.7, `mlflow` 3.18.0, `pandas` 3.0.6, `scikit-learn` 1.9.1, `joblib` 1.6.0, `numpy` 2.5.5 (versions de l'énoncé). Données : `train-metadata.csv` de S2, 257 543 161 octets, `sha256` `536e8208cfb3502b…` (le prérequis 1 est vérifié). Rappel cible : **0,95** (décision de S2, voir `JOURNAL.md`).

## Mesure 1 — Découpages

| Grandeur | Valeur |
|---|---|
| Lignes de test et positifs en test, graine 42 | 100 054 lignes, 130 positifs (261 patients) |
| Lignes de test et positifs en test, graine 7 | 101 995 lignes, 108 positifs (261 patients) |
| 12 premiers caractères de l'empreinte de `donnees/manifeste.json` | `95f701733ed6` |

Le jeu compte 401 059 lignes, 393 positifs, 1 042 patients. Intersection vide entre entraînement et test pour les deux graines (contrôle de `preparer.py`).

**Question 1.1.** `GroupShuffleSplit` tire 25 % des *patients* (261 sur 1 042), pas 25 % des lignes ; or un patient porte de 1 à 9 184 lésions et les 393 positifs se concentrent sur 259 patients, donc les lignes et les positifs du test dépendent des patients tirés.

## Mesure 2 — Premier run (référence, graine 42)

```
reference-g42  PR-AUC 0.0506  precision@95% 0.0028  seuil 0.1665  11 s  run 8d6c4a1da35b45bea36dd783dd2bd357
```

| Grandeur | Valeur |
|---|---|
| PR-AUC | 0,0506 |
| Précision au rappel cible | 0,0028 |
| Seuil | 0,16646103735842746 |
| Durée d'entraînement | 11 s (53,3 s pour la commande complète, imports compris) |
| Identifiant du run | `8d6c4a1da35b45bea36dd783dd2bd357` |
| Rappel atteint au seuil | 0,9538 |
| Modèle | `model/reference-g42/modele.joblib`, 10 185 octets, `sha256` `c56a7555a1412703…` |

**Question 1.2.** Mon seuil de S2 vaut 0,1714487 (PR-AUC 0,0553) et celui-ci 0,1665 (PR-AUC 0,0506) : ils sont proches, pas égaux. Le seuil dépend de l'ensemble de test, et celui-ci n'est pas le même (S2 : 20 % des patients, 209 patients, 81 545 lignes, 110 positifs ; ici 25 % des patients, 261 patients, 100 054 lignes, 130 positifs), donc l'égalité n'était pas attendue. Elle aurait prouvé que la chaîne se rejoue à l'identique, alors que cette différence prouve seulement que le découpage a changé ; l'ordre de grandeur et les 40 colonnes sont conservés, mais je n'ai pas rejoué le découpage de S2, donc la reproductibilité exacte n'est pas démontrée par cette mesure.

## Mesure 3 — Le suivi voyage avec le paquet

Les observations sont lues sur le suivi de `poste/` par `outils/outils_s6.py sonde` (lecture par l'API MLflow, la même base que l'interface), avant puis après `importer_suivi.py`.

| Observation | Avant `importer_suivi.py` | Après |
|---|---|---|
| Les métriques et paramètres du run sont-ils lisibles ? | Oui : 5 métriques, 7 paramètres, tag `sha256_manifeste` `95f701733ed6` | Oui |
| Les artefacts (`model/modele.joblib`) sont-ils lisibles ? | **Non** : `MlflowException : Failed to download artifacts from path 'modele.joblib'` | **Oui** |
| Chemin indiqué pour les artefacts, dans les détails du run | `file:///C:/Users/pelli/Documents/workspace/M2/Indus%20de%20l%20ia%20dans%20le%20cloud/TP6/s6-pellicano/session/suivi/artefacts/8d6c4a1da35b45bea36dd783dd2bd357/artifacts` | même chemin avec `poste/` à la place de `session/` |

`importer_suivi.py` a réécrit 1 ligne dans `experiments.artifact_location` et 1 ligne dans `runs.artifact_uri` ; 0 ligne dans `model_versions` (aucune version n'existait encore). Un second passage affiche « rien a reecrire ».

**Question 1.3.**
(a) Les métriques et les paramètres sont des lignes de `suivi/mlflow.db`, copiée avec le zip ; les artefacts sont des fichiers dont la base mémorise l'emplacement en chemin absolu (`…/session/suivi/artefacts/…`), et ce dossier avait été renommé `session_fermee`, donc la base pointait vers un chemin qui n'existe plus.
(b) `importer_suivi.py` remplace le préfixe de l'ancien dossier par celui de `poste/suivi/artefacts` dans `experiments.artifact_location`, `runs.artifact_uri` et, quand il y en a, `model_versions.source` et `storage_location`.
(c) Entre deux postes d'un groupe, le chemin absolu change (nom d'utilisateur, lecteur, dossier du dépôt) : la même rupture se reproduirait à chaque transfert, sauf à relancer l'import sur le poste qui reçoit.

## Mesure 4 — Vue de comparaison (quatre runs)

Les valeurs viennent de `poste/comparaison_runs.csv`, écrit par `outils_s6.py comparer` à partir de la base ; la vue de l'interface est en `captures/01_comparaison_4_runs.png` (quatre runs comparés) et `captures/02_comparaison_metriques.png` (tableaux des paramètres et des métriques, valeurs arrondies à trois décimales par l'interface).

| Run | PR-AUC | Précision au rappel cible | Durée d'entraînement |
|---|---|---|---|
| reference-g42 | 0,0506 | 0,0028 | 11,2 s |
| reference-g7 | 0,0653 | 0,0025 | 11,0 s |
| variante-g42 | 0,0834 | 0,0023 | 2,2 s |
| variante-g7 | 0,0469 | 0,0035 | 1,8 s |

La colonne « Durée d'entraînement » est la métrique `duree_entrainement_s` (temps de `fit` seul). La ligne « Duration » de l'interface est plus longue, car elle couvre tout le run (11,8 s, 11,6 s, 2,8 s, 2,3 s), journalisation des artefacts comprise ; les deux classent les approches dans le même ordre.

Rappel atteint : 0,9538 (graine 42, 124 positifs sur 130) et 0,9537 (graine 7). Seuils : 0,1665 / 0,1917 (référence), 0,0322 / 0,1273 (variante).

## Mesure 5 — Écarts (métrique d'arbitrage : précision au rappel cible)

| Grandeur | Valeur |
|---|---|
| Écart variante − référence, graine 42 | − 0,000491 (− 17,3 %) |
| Écart variante − référence, graine 7 | + 0,001029 (+ 41,3 %) |
| Variation de la référence entre ses deux graines | 0,000345 |
| Variation de la variante entre ses deux graines | 0,001175 |

**Question 1.4.** Non : l'écart entre approches ne dépasse pas la variation d'une même approche, il change même de signe (− 0,0005 à la graine 42, + 0,0010 à la graine 7) et reste sous la variation de la variante (0,0012). Aucune des trois conditions de `JOURNAL.md` n'est remplie : je ne peux pas dire que la variante est meilleure. Le critère de départage (durée d'entraînement) désigne la variante : 2,2 s et 1,8 s contre 11,2 s et 11,0 s ; je promeus donc **variante-g42** au coût, non à la performance. J'attendais que le gradient boosting batte la régression logistique : les mesures ne le montrent pas, et sur la graine promue la variante a même une précision plus basse (0,0023 contre 0,0028). Le classement par PR-AUC changerait de sens d'une graine à l'autre, lui aussi (0,0834 contre 0,0506, puis 0,0469 contre 0,0653).

## Mesure 6 — Registre et chaîne de traçabilité

Promotions faites avec `promouvoir.py --validateur "Théo Pellicano"`, `ALIAS_SERVI = "production"`, `ALIAS_REPLI = "repli"` : `reference-g42` d'abord (v1), puis `variante-g42` (v2).

```
dermascan-tabulaire v1 -> production (run reference-g42, valide par Théo Pellicano) ; repli : aucune
dermascan-tabulaire v2 -> production (run variante-g42, valide par Théo Pellicano) ; repli : 1
```

`verifier_chaine.py model/variante-g42/modele.joblib` (code de sortie 0) :

```
registre : dermascan-tabulaire v2, valide par Théo Pellicano, repli 1
OK  fichier servi = version promue     8bce13332b327e6c
run : variante-g42  graine 42  PR-AUC 0.0834
OK  artefact du run = fichier servi    8bce13332b327e6c
OK  manifeste du run = manifeste local 95f701733ed60955
OK  donnees du manifeste = donnees locales 536e8208cfb3502b
commit du code qui a produit les donnees : hors-git
```

| Grandeur | Valeur |
|---|---|
| Version promue | `dermascan-tabulaire` v2 (alias `production`), run `variante-g42` |
| Version de repli | v1 (alias `repli`), run `reference-g42` |
| Maillon 1 — fichier servi = version promue | OK (`8bce13332b327e6c`) |
| Maillon 2 — artefact du run = fichier servi | OK |
| Maillon 3 — manifeste du run = manifeste local | OK (`95f701733ed60955`) |
| Maillon 4 — données du manifeste = données locales | OK (`536e8208cfb3502b`) |
| Commit du code | `hors-git` (affiché, non contrôlé par le script) |

Le registre vu dans l'interface (versions, alias, validateur, repli, empreintes) est en `captures/03_registre_modeles.png`.

Avec l'autre fichier (`model/reference-g42/modele.joblib`) :

```
registre : dermascan-tabulaire v2, valide par Théo Pellicano, repli 1
KO  fichier servi = version promue     c56a7555a1412703  (attendu 8bce13332b327e6c)
code de sortie : 1
```

**Question 1.5.** Le premier maillon rompt : l'empreinte du fichier servi (`c56a7555…`) n'est pas celle de la version promue (`8bce1333…`), et le code de sortie est 1. Le script s'arrête au premier maillon rompu avec un code non nul sans que personne ait à lire la sortie, donc un pipeline le traite comme un test (exigence H2). Je le lancerais en intégration continue juste avant `docker build`, une fois `model/` copié dans le contexte de build, pour qu'un mauvais fichier bloque le push de l'image, et une seconde fois sur le fichier présent dans l'image construite.

## Écarts avec l'énoncé

| Écart | Raison |
|---|---|
| `RAPPEL_CIBLE = 0.95` au lieu de 0.90 dans `entrainer_suivi.py` | Le fichier distribué portait 0.90 « comme en S2 », alors que mon rappel visé de S2 est 0,95 (voir `JOURNAL.md`). |
| `entrainer_suivi.py` écrit l'emplacement des artefacts sous forme d'URI (`Path("suivi/artefacts").resolve().as_uri()`) et `importer_suivi.py` calcule le nouveau préfixe de la même façon | Sous Windows, le chemin absolu est `C:\…` et non `/…/suivi/artefacts` : l'URI `file:///C:/…` est la forme que MLflow sait relire et que l'import peut réécrire. Les autres blancs sont remplis comme demandé : `SUIVI = "sqlite:///suivi/mlflow.db"`, tag `sha256_manifeste` = `meta["sha256_manifeste"]`, alias `production` et `repli`. |
| Export et import du zip faits avec `python -m zipfile` | `zip` et `unzip` n'existent pas sous PowerShell 5.1 ; le module de Python produit un zip aux séparateurs corrects. |
| Mesure 3 relevée par `outils_s6.py sonde` et non dans l'onglet Artifacts | La base lue est la même que celle de l'interface ; le script donne le texte exact de l'erreur. |
| Validateur saisi `Théo Pellicano` | Nom du validateur au registre : une personne, comme le demande le tableau de décisions. |

Les fichiers de séance avec leurs blancs remplis sont dans `fichiers-seance/` ; `outils/outils_s6.py` lit le suivi (sonde, comparaison, registre).
