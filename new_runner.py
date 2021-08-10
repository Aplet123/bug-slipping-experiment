import hypothesis
from hypothesis import (
    example,
    Phase,
    settings,
    Verbosity,
    given,
    strategies as st,
    HealthCheck,
    seed,
)
import itertools
from multiprocessing import Process, Queue, cpu_count, set_start_method
from new_mutagen import Mutagen
from os import path
from types import SimpleNamespace
from copy import deepcopy
import json
from tqdm import tqdm
from base64 import b64encode
import plyvel
import pickle

# stop hypothesis from printing error tracebacks
object.__setattr__(
    hypothesis._settings.default_variable.value, "verbosity", Verbosity.quiet
)

with_shrink = (Phase.explicit, Phase.reuse, Phase.generate, Phase.target, Phase.shrink)
without_shrink = (Phase.explicit, Phase.reuse, Phase.generate, Phase.target)


names = {1: "single", 2: "double", 3: "triple", 4: "quadruple"}

modname = "toml"
to_shrink = False
ncombos = 1

filename = f"data/{modname}_{names.get(ncombos, 'x' + str(ncombos))}_{('unshrunk', 'shrunk')[to_shrink]}"


def generate_module(mg):
    with open(path.join(path.dirname(__file__), modname + ".py")) as f:
        code = f.read()
    vals = {"mg": mg}
    exec(code, vals)
    ret = SimpleNamespace()
    for (k, v) in vals.items():
        setattr(ret, k, v)
    # print(ret)
    return ret


default_module = generate_module(Mutagen())
default_mg = deepcopy(default_module.mg)


def gen_mutants(mutants):
    mg = deepcopy(default_mg)
    mg.current_mutants = set(mutants)
    return generate_module(mg)


def run_test(
    module,
    seed_to_use=None,
    phase=without_shrink,
    examples=10000,
    additional_settings={},
):
    # print("starting test")
    fails = []
    attempts = 0

    @seed(seed_to_use)
    @given(module.testing_strategy)
    @settings(
        verbosity=Verbosity.quiet,
        phases=phase,
        max_examples=examples,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
        database=None,
        **additional_settings,
    )
    def f(x):
        nonlocal attempts
        if len(fails) == 0:
            attempts += 1
        try:
            module.testing_function(deepcopy(x))
        except BaseException as e:
            # tqdm.write(f"hmm {module.mg.current_mutants} {x}")
            fails.append(deepcopy(x))
            raise

    try:
        f()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        pass
    # print("ending test")
    return (fails, attempts)


def triage_failure(module, mutants, data):
    bs = set()
    for l in range(1, len(mutants) + 1):
        for s in itertools.combinations(mutants, l):
            s = set(s)
            if not any(x <= s for x in bs):
                module.mg.current_mutants = s
                try:
                    module.testing_function(deepcopy(data))
                except KeyboardInterrupt:
                    raise
                except BaseException as e:
                    bs.add(frozenset(s))
    return bs


def run_jobs(jobs, data_queue, test_settings={}, pbar=None, thread_name="?"):
    # print("thread started")
    data = {}
    testing_module = generate_module(Mutagen())
    pepega = 0
    for job in jobs:
        # tqdm.write("starting job " + str(pepega))
        pepega += 1
        k = "|".join(job)
        if pbar is not None:
            pbar.set_description(f"thread {thread_name} ({k})")
        testing_module.mg.current_mutants = job
        (fails, attempts) = run_test(testing_module, **test_settings)
        if len(fails) > 0:
            fail = fails[-1]
            triage = [list(x) for x in triage_failure(testing_module, job, fail)]
            data[k] = {
                "type": "fail",
                "attempts": attempts,
                "fail": b64encode(pickle.dumps(fail)).decode("utf8"),
                "triage": triage,
                "fail_repr": repr(fail),
            }
        else:
            data[k] = {
                "type": "nofail",
                "attempts": attempts
            }
        if pbar is not None:
            pbar.update()
    data_queue.put(data)
    # current_process().kill()
    # print("done terminating")


def run_combos(combos, nthreads=3, test_settings={}, pbar_offset=0):
    data_queue = Queue()
    jobs = [[] for _ in range(nthreads)]
    muts = default_mg.all_mutants
    for (i, combo) in enumerate(itertools.combinations(muts, combos)):
        jobs[i % nthreads].append(set(combo))
    pbars = [
        tqdm(total=len(x), position=i + pbar_offset, leave=False)
        for (i, x) in enumerate(jobs)
    ]
    threads = []
    for (i, (job, pbar)) in enumerate(zip(jobs, pbars)):
        thread = Process(
            target=run_jobs,
            args=(job, data_queue),
            kwargs={"test_settings": test_settings, "pbar": pbar, "thread_name": i},
        )
        pbar.set_description(f"thread {i}")
        threads.append(thread)
    for thread in threads:
        thread.start()
    data = {}
    for _ in range(nthreads):
        data.update(data_queue.get())
    for thread in threads:
        thread.join()
    for pbar in pbars:
        pbar.close()
    return data

# def compute_probability(data):



if __name__ == "__main__":
    total_data = {}
    nseeds = 100
    total_pbar = tqdm(range(1, nseeds + 1), position=0)
    total_pbar.set_description("overall")
    db = plyvel.DB(f"{filename}_ldb", create_if_missing=True)
    override = (input("Override existing results? [y/N] ").strip().lower() or "n")[0] == "y"
    for seed_to_use in total_pbar:
        key = str(seed_to_use).encode("utf8")
        if not override:
            existing = db.get(key)
            if existing is not None:
                total_data[seed_to_use] = json.loads(existing.decode("utf8"))
                continue
        res = run_combos(
            ncombos,
            test_settings={
                "phase": (without_shrink, with_shrink)[to_shrink],
                "examples": 500,
                "seed_to_use": seed_to_use,
            },
            nthreads=max(cpu_count() - 1, 1),
            pbar_offset=1,
        )
        total_data[seed_to_use] = res
        db.put(str(seed_to_use).encode("utf8"), json.dumps(res, sort_keys=True).encode("utf8"))
        # print(seed_to_use, total_data[seed_to_use])
    db.close()
    with open(filename + ".json", "w") as f:
        json.dump(total_data, f, sort_keys=True)
