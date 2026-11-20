"""Seance 6 — outils de lecture du suivi (sans reseau), a lancer depuis poste/.

    python outils_s6.py sonde            # metriques lisibles ? artefacts lisibles ? chemin des artefacts
    python outils_s6.py runid <nom>      # identifiant du run (ex. reference-g42)
    python outils_s6.py comparer         # mesures 4 et 5 + ecriture de comparaison_runs.csv
    python outils_s6.py registre         # versions du registre, alias, tags (validateur, repli, empreinte)
"""
import csv
import sys

from mlflow import MlflowClient

SUIVI = "sqlite:///suivi/mlflow.db"
EXPERIENCE = "dermascan-tabulaire"
ORDRE = ["reference-g42", "reference-g7", "variante-g42", "variante-g7"]


def runs():
    c = MlflowClient(SUIVI)
    exp = c.get_experiment_by_name(EXPERIENCE)
    if exp is None:
        sys.exit(f"experience {EXPERIENCE} introuvable dans ce suivi")
    return c, {r.info.run_name: r for r in c.search_runs([exp.experiment_id])}


def sonde():
    c, rs = runs()
    for nom in ORDRE:
        if nom not in rs:
            continue
        r = rs[nom]
        print(f"run {nom} ({r.info.run_id})")
        print(f"  metriques lisibles : {len(r.data.metrics)} ({', '.join(sorted(r.data.metrics))})")
        print(f"  parametres lisibles : {len(r.data.params)}")
        print(f"  tags sha256_manifeste : {r.data.tags.get('sha256_manifeste', '')[:12]}")
        print(f"  chemin des artefacts (artifact_uri) : {r.info.artifact_uri}")
        try:
            chemin = c.download_artifacts(r.info.run_id, "model/modele.joblib")
            print(f"  artefact model/modele.joblib : LISIBLE ({chemin})")
        except Exception as e:  # noqa: BLE001 - on veut le message tel quel
            print(f"  artefact model/modele.joblib : ILLISIBLE ({type(e).__name__} : {str(e)[:160]})")


def comparer():
    _, rs = runs()
    manque = [n for n in ORDRE if n not in rs]
    if manque:
        sys.exit(f"runs manquants : {manque}")
    m = {n: rs[n].data.metrics for n in ORDRE}
    print(f"{'run':<15}{'PR-AUC':>10}{'precision@rappel cible':>25}{'rappel':>9}{'seuil':>12}{'duree (s)':>11}")
    lignes = []
    for n in ORDRE:
        x = m[n]
        print(f"{n:<15}{x['pr_auc']:>10.4f}{x['precision_au_seuil']:>25.4f}{x['rappel_au_seuil']:>9.4f}"
              f"{x['seuil']:>12.6f}{x['duree_entrainement_s']:>11.1f}")
        lignes.append({"run": n, "run_id": rs[n].info.run_id, **{k: x[k] for k in
                       ["pr_auc", "precision_au_seuil", "rappel_au_seuil", "seuil", "duree_entrainement_s"]}})
    with open("comparaison_runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    p = {n: m[n]["precision_au_seuil"] for n in ORDRE}
    print()
    print("Mesure 5 (metrique d'arbitrage = precision_au_seuil)")
    e42 = p["variante-g42"] - p["reference-g42"]
    e7 = p["variante-g7"] - p["reference-g7"]
    vr = abs(p["reference-g42"] - p["reference-g7"])
    vv = abs(p["variante-g42"] - p["variante-g7"])
    print(f"  ecart variante - reference, graine 42 : {e42:+.6f}")
    print(f"  ecart variante - reference, graine 7  : {e7:+.6f}")
    print(f"  variation de la reference entre graines : {vr:.6f}")
    print(f"  variation de la variante entre graines  : {vv:.6f}")
    bruit = max(vr, vv)
    print()
    print("Regle ecrite dans JOURNAL.md (trois conditions)")
    print(f"  (a) ecart positif aux deux graines : {e42 > 0 and e7 > 0}")
    print(f"  (b) ecart > plus grande variation intra-approche ({bruit:.6f}) aux deux graines : "
          f"{abs(e42) > bruit and abs(e7) > bruit}")
    r42 = e42 / p["reference-g42"]
    r7 = e7 / p["reference-g7"]
    print(f"  (c) ecart relatif a la reference >= +20 % : g42 {r42:+.1%}, g7 {r7:+.1%} -> {r42 >= 0.2 and r7 >= 0.2}")
    d = {n: m[n]["duree_entrainement_s"] for n in ORDRE}
    print(f"  critere de departage, duree : reference {d['reference-g42']:.1f}/{d['reference-g7']:.1f} s, "
          f"variante {d['variante-g42']:.1f}/{d['variante-g7']:.1f} s")


def registre():
    c = MlflowClient(SUIVI)
    nom = "dermascan-tabulaire"
    alias = {}
    for a in ("production", "repli"):
        try:
            alias[a] = c.get_model_version_by_alias(nom, a).version
        except Exception:  # noqa: BLE001
            alias[a] = None
    print(f"modele {nom} : alias production -> v{alias['production']}, repli -> v{alias['repli']}")
    for v in sorted(c.search_model_versions(f"name='{nom}'"), key=lambda v: int(v.version)):
        run = c.get_run(v.run_id)
        print(f"  v{v.version}  run {run.info.run_name} ({v.run_id[:12]})  valide par {v.tags.get('validateur')}  "
              f"repli {v.tags.get('repli')}  sha256_modele {v.tags.get('sha256_modele', '')[:12]}")
        print(f"      source {v.source}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "sonde":
        sonde()
    elif sys.argv[1] == "runid":
        print(runs()[1][sys.argv[2]].info.run_id)
    elif sys.argv[1] == "comparer":
        comparer()
    elif sys.argv[1] == "registre":
        registre()
    else:
        sys.exit(__doc__)
