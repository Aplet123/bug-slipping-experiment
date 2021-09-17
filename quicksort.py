# register mutants
mg.register_mutant("ONLY_ADD_ONE_PIVOT", description="Only adds the pivot once if there are multiple.") # description is optional
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
