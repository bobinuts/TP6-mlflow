# JOURNAL — Séance 6 (suivre, gouverner, préparer)

Théo Pellicano · M2 IA & Data · YNOV Campus Montpellier · 20/11/2026

## Décisions de comparaison — écrites le 20/11/2026 à 12:08, avant tout entraînement

Aucun entraînement, aucun découpage, aucun appel de `preparer.py` n'avait été lancé à cette heure.

| Décision | Valeur | Raison |
|---|---|---|
| Métrique d'arbitrage entre deux approches | `precision_au_seuil` : précision obtenue au seuil qui atteint le rappel cible, sur le test (plus haute = meilleure) | L'exigence métier est fixe (le rappel). Le coût est le nombre de lésions examinées par maligne, soit 1 / précision (S2 : 341, S4 : 422). C'est la grandeur que le projet ISIC arbitre « à rappel fixé ». |
| Rappel cible | **0,95** | Décision de S2 (09/10/2026, 11:31), conservée. Le fichier `entrainer_suivi.py` distribué portait `RAPPEL_CIBLE = 0.90` avec le commentaire « comme en S2 » : une seule constante est changée, et l'écart est assumé. |
| Écart minimal pour déclarer une approche meilleure | La variante est déclarée meilleure seulement si **les trois conditions** sont vraies : (a) l'écart variante − référence est positif aux deux graines ; (b) il dépasse, aux deux graines, la plus grande variation observée entre les deux graines pour une même approche (en valeur absolue, sur la métrique d'arbitrage) ; (c) il vaut au moins **+ 20 %** de la précision de la référence à la même graine | (b) confronte l'écart au bruit, comme le demande la partie 1.4. (c) écarte un gain réel mais trop faible pour changer le nombre de lésions examinées. |
| Critère de départage si l'écart est sous le bruit | `duree_entrainement_s` (enregistrée par le run) : on garde l'approche la moins coûteuse à entraîner ; à durée comparable, la référence | La durée est une grandeur du run, mesurée de la même façon pour les quatre runs ; elle ne dépend pas du résultat. |
| Nom du validateur au registre | Théo Pellicano | Une personne, pas un rôle. |
| Graine promue | 42 ; la graine 7 sert à estimer le bruit | Fixée avant de voir les résultats, pour ne pas choisir la graine qui arrange. |
| Découpage | par `patient_id`, 25 % des patients en test (valeur de `preparer.py`), graines 42 et 7 | Un patient ne peut pas être des deux côtés (S2). |

**Limite connue de la règle.** Deux graines donnent une estimation grossière du bruit (n = 2) : la variation mesurée peut être plus faible ou plus forte que la vraie. Elle ne couvre que la variabilité du découpage (et le tirage interne de la variante), pas celle des données elles-mêmes.

## Question 0.1

Un écart de métrique sera réel si la variante bat la référence aux deux graines, avec un écart plus grand que la plus grande variation d'une même approche entre ces deux graines.
Il devra aussi valoir au moins + 20 % de la précision de la référence ; sinon, il est sous le bruit et la décision se prend sur la durée d'entraînement.
