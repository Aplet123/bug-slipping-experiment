import plyvel
import json
from tqdm import tqdm
import matplotlib.pyplot as plt

names = {1: "single", 2: "double", 3: "triple", 4: "quadruple"}

modname = "btree"

def rearrange_keys(d):
    ret = {}
    for k in d:
        if modname == "toml" and any(x in k for x in ("BAD_CIRCULAR_REF_CHECK", "STR_NO_LEADING_DOT")):
            continue
        ret["|".join(sorted(k.split("|")))] = d[k]
    return ret

bugs_unshrunk = {}
bugs_shrunk = {}
for ncombos in range(1, 4):
    unshrunk_db = plyvel.DB(
        f"data/{modname}_{names.get(ncombos, 'x' + str(ncombos))}_unshrunk_ldb"
    )
    shrunk_db = plyvel.DB(
        f"data/{modname}_{names.get(ncombos, 'x' + str(ncombos))}_shrunk_ldb"
    )
    for seed in tqdm(range(1, 101)):
        key = str(seed).encode("utf8")
        unshrunk_data = rearrange_keys(json.loads(unshrunk_db.get(key)))
        shrunk_data = rearrange_keys(json.loads(shrunk_db.get(key)))
        for k in unshrunk_data:
            for bug in k.split("|"):
                if bug not in bugs_unshrunk:
                    bugs_unshrunk[bug] = [0, 0]
                bugs_unshrunk[bug][1] += 1
                if bug not in bugs_shrunk:
                    bugs_shrunk[bug] = [0, 0]
                bugs_shrunk[bug][1] += 1
            unshrunk_entry = unshrunk_data[k]
            shrunk_entry = shrunk_data[k]
            if unshrunk_entry["type"] == "fail":
                for bugs in unshrunk_entry["triage"]:
                    for bug in bugs:
                        bugs_unshrunk[bug][0] += 1
            if shrunk_entry["type"] == "fail":
                for bugs in shrunk_entry["triage"]:
                    for bug in bugs:
                        bugs_shrunk[bug][0] += 1

bugs = list(bugs_unshrunk.keys())
ratios = []
for ncombos in range(1, 4):
    unshrunk_db = plyvel.DB(
        f"data/{modname}_{names.get(ncombos, 'x' + str(ncombos))}_unshrunk_ldb"
    )
    shrunk_db = plyvel.DB(
        f"data/{modname}_{names.get(ncombos, 'x' + str(ncombos))}_shrunk_ldb"
    )
    for seed in tqdm(range(1, 101)):
        key = str(seed).encode("utf8")
        unshrunk_data = rearrange_keys(json.loads(unshrunk_db.get(key)))
        shrunk_data = rearrange_keys(json.loads(shrunk_db.get(key)))
        for k in unshrunk_data:
            unshrunk_entry = unshrunk_data[k]
            shrunk_entry = shrunk_data[k]
            if not (
                unshrunk_entry["type"] == shrunk_entry["type"]
                and (unshrunk_entry["type"] == "nofail" or unshrunk_entry["attempts"] == shrunk_entry["attempts"])
            ):
                print("rut roh")
                print(seed, k, unshrunk_entry, shrunk_entry)
                raise Exception("wtmoo")
            if unshrunk_entry["type"] != "fail":
                continue
            prob_pre = min(bugs_unshrunk[bug][0] / bugs_unshrunk[bug][1] for bugs in unshrunk_entry["triage"] for bug in bugs)
            prob_post = min(bugs_shrunk[bug][0] / bugs_shrunk[bug][1] for bugs in unshrunk_entry["triage"] for bug in bugs)
            ratio = prob_post / prob_pre
            ratios.append(ratio)

plt.hist(ratios)
plt.show()