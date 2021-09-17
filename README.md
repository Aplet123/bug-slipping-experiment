# Bug Slippage Experiments

## Adapting a new module
Let's look at a hypothetical `quicksort` module. It might look something like this prior to mutant injection:
```py
def quicksort(l):
    if len(l) <= 1:
        return l
    pivot = l[0]
    lo = quicksort([x for x in l if x < pivot])
    pivots = [x for x in l if x == pivot]
    hi = quicksort([x for x in l if x > pivot])
    return lo + pivots + hi
```
Now, we can use a modified version of the pytest_mutagen module to inject mutants. The runner will define a variable `mg` that will already contain this mutagen instance:
```py
# register mutants
mg.register_mutant("ONLY_ADD_ONE_PIVOT", "Only adds the pivot once if there are multiple.") # description is optional
mg.register_mutant("NO_SORT_LEN_2_LISTS")

def quicksort(l):
    # you can use mg.mut(mutant_name, inactive_value, active_value) to generate a value based on a mutant
    # if the mutant is active, it'll evaluate to active_value()
    # if the mutant is inactive, it'll evaluate to inactive_value()
    if len(l) <= mg.mut("NO_SORT_LEN_2_LISTS", lambda: 1, lambda: 2):
        return l
    pivot = l[0]
    lo = quicksort([x for x in l if x < pivot])
    # you can also test for mutants directly with mg.active_mutant(mutant_name) and mg.not_mutant(mutant_name)
    if mg.active_mutant("ONLY_ADD_ONE_PIVOT"):
        pivots = [x for x in l if x == pivot]
    hi = quicksort([x for x in l if x > pivot])
    return lo + pivots + hi
```

Now we have to add the hypothesis testing strategy and testing function, which the runner will retrieve from the variables `testing_strategy` and `testing_function`, respectively.
```py
# register mutants
mg.register_mutant("ONLY_ADD_ONE_PIVOT", "Only adds the pivot once if there are multiple.") # description is optional
mg.register_mutant("NO_SORT_LEN_2_LISTS")

def quicksort(l):
    # you can use mg.mut(mutant_name, inactive_value, active_value) to generate a value based on a mutant
    # if the mutant is active, it'll evaluate to active_value()
    # if the mutant is inactive, it'll evaluate to inactive_value()
    if len(l) <= mg.mut("NO_SORT_LEN_2_LISTS", lambda: 1, lambda: 2):
        return l
    pivot = l[0]
    lo = quicksort([x for x in l if x < pivot])
    # you can also test for mutants directly with mg.active_mutant(mutant_name) and mg.not_mutant(mutant_name)
    if mg.active_mutant("ONLY_ADD_ONE_PIVOT"):
        pivots = [x for x in l if x == pivot]
    hi = quicksort([x for x in l if x > pivot])
    return lo + pivots + hi

from hypothesis import strategies as st

testing_strategy = st.lists(st.integers())

def testing_function(l):
    sorted_list = quicksort(l)
    for i in range(len(sorted_list) - 1):
        assert sorted_list[i] <= sorted_list[i + 1]
```
Now the program is ready to be run. You should adjust the commented values at the top of `new_runner.py` to match the module. So, if the file is saved into `quicksort.py`, the start of the file might look something like this:
```py
# change these four values
# the module the code is in (if set to btree, it will open btree.py in the current directory)
modname = "quicksort"
# if shrinking should be performed or not
to_shrink = False
# the number of mutants to use (1 = single mutant runs, 2 = double mutant runs, etc.)
ncombos = 1
# the number of seeds to use (probably don't need to change)
nseeds = 100
```
