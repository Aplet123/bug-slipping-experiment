import new_runner
import pickle
from base64 import b64encode
import plyvel
from copy import deepcopy
import json

def rearrange_keys(d):
    ret = {}
    for k in d:
        ret["|".join(sorted(k.split("|")))] = d[k]
    return ret

new_runner.modname = "toml"
new_runner.to_shrink = True
damaged_key = "BAD_CIRCULAR_REF_CHECK|NO_PARSE_LONE_QUOTE"
seed_to_use = 14

job = set(damaged_key.split("|"))
new_runner.ncombos = len(job)
new_runner.filename = f"data/{new_runner.modname}_{new_runner.names.get(new_runner.ncombos, 'x' + str(new_runner.ncombos))}_{('unshrunk', 'shrunk')[new_runner.to_shrink]}"
mod = new_runner.generate_module(new_runner.Mutagen())
mod.mg.current_mutants = deepcopy(job)
assert len(mod.mg.current_mutants) == new_runner.ncombos
phase = (new_runner.without_shrink, new_runner.with_shrink)[new_runner.to_shrink]
db = plyvel.DB(f"{new_runner.filename}_ldb", create_if_missing=False)
key = str(seed_to_use).encode("utf8")
(fails, attempts) = new_runner.run_test(mod, seed_to_use, phase, 500)
entry = rearrange_keys(json.loads(db.get(key)))
if len(fails) > 0:
    fail = fails[-1]
    triage = [list(x) for x in new_runner.triage_failure(mod, job, fail)]
    data = {
        "type": "fail",
        "attempts": attempts,
        "fail": b64encode(pickle.dumps(fail)).decode("utf8"),
        "triage": triage,
        "fail_repr": repr(fail),
    }
else:
    data = {
        "type": "nofail",
        "attempts": attempts
    }
if entry[damaged_key] == data:
    print("unchanged")
entry[damaged_key] = data
db.put(key, json.dumps(entry).encode("utf8"))
