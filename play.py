import plyvel

import plyvel
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
import itertools
from collections import defaultdict
import math

names = {1: "single", 2: "double", 3: "triple", 4: "quadruple"}

modname = "avltree"

def rearrange_keys(d):
    ret = {}
    for k in d:
        if modname == "toml" and any(x in k for x in ("BAD_CIRCULAR_REF_CHECK", "STR_NO_LEADING_DOT")):
            continue
        ret["|".join(sorted(k.split("|")))] = d[k]
    return ret

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
            if any(len(x) > 1 for x in unshrunk_entry["triage"]) or any(len(x) > 1 for x in shrunk_entry["triage"]):
                print("huh", k, unshrunk_entry, shrunk_entry)
            