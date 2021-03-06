# ------------- IMPORTS ------------

from new_mutagen import Mutagen
from hypothesis import example, Phase, settings, Verbosity, given, strategies as st, HealthCheck
import json

mg = Mutagen()

#
# B-tree set (Python)
#
# Copyright (c) 2020 Project Nayuki. (MIT License)
# https://www.nayuki.io/page/btree-set
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# - The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# - The Software is provided "as is", without warranty of any kind, express or
#   implied, including but not limited to the warranties of merchantability,
#   fitness for a particular purpose and noninfringement. In no event shall the
#   authors or copyright holders be liable for any claim, damages or other
#   liability, whether in an action of contract, tort or otherwise, arising from,
#   out of or in connection with the Software or the use or other dealings in the
#   Software.
#


# ****************************************** MUTANTS ******************************************

# Blank mutant
# @mg.has_mutant("NO_MUTANT", "btree.py")

# --------------- BTreeSet ----------------

# Function: clear

@mg.has_mutant("CLEAR_NO_SIZE_UPDATE", "btree.py")

# Function: add

@mg.has_mutant("ADD_NO_CHILD_UPDATE", "btree.py")
@mg.has_mutant("ADD_NO_SIZE_UPDATE", "btree.py")
@mg.has_mutant("ADD_NO_SPLIT_INDEX", "btree.py")
@mg.has_mutant("ADD_GTE_RPL_GT", "btree.py")
@mg.has_mutant("ADD_GT_RPL_GTE", "btree.py")
@mg.has_mutant("ADD_CHILD_WRONG_UPDATE", "btree.py")

# Function: remove

@mg.has_mutant("REMOVE_GT_RPL_GTE", "btree.py")
@mg.has_mutant("REMOVE_NO_SIZE_CHECK", "btree.py")
@mg.has_mutant("REMOVE_NO_SIZE_UPDATE", "btree.py")
@mg.has_mutant("REMOVE_NO_NODE_ROOT_CMP", "btree.py")
@mg.has_mutant("REMOVE_FLIP_DEC_HEIGHT", "btree.py")
@mg.has_mutant("REMOVE_NO_INDEX_UPDATE", "btree.py")
@mg.has_mutant("REMOVE_LR_WRONG_ASSGN", "btree.py")

# --------------- Node ----------------

# Function: __init__

@mg.has_mutant("NODE_INIT_GT_RPL_GTE", "btree.py")

# Function: search

@mg.has_mutant("NODE_SEARCH_GT_RPL_GTE", "btree.py")
@mg.has_mutant("NODE_SEARCH_LT_RPL_LTE", "btree.py")
@mg.has_mutant("NODE_SEARCH_GTE_RPL_GT_1", "btree.py")
@mg.has_mutant("NODE_SEARCH_GTE_RPL_GT_2", "btree.py")

# Function: split_child

@mg.has_mutant("NODE_SPLT_CH_CHILD_INSERT_WRNG", "btree.py")
@mg.has_mutant("NODE_SPLT_CH_L_CH_EXT_WRNG", "btree.py")
@mg.has_mutant("NODE_SPLT_CH_R_CH_EXT_WRNG", "btree.py")
@mg.has_mutant("NODE_SPLT_CH_R_KEYS_EXT_WRNG", "btree.py")

# Function: ensure_child_remove

@mg.has_mutant("ECR_GT_RPL_GTE_1", "btree.py")
@mg.has_mutant("ECR_GT_RPL_GTE_2", "btree.py")
@mg.has_mutant("ECR_GTE_RPL_GT_1", "btree.py")
@mg.has_mutant("ECR_GTE_RPL_GT_2", "btree.py")
@mg.has_mutant("ECR_L_SBLNG_WRNG", "btree.py")
@mg.has_mutant("ECR_R_SBLNG_WRNG", "btree.py")
@mg.has_mutant("ECR_CHLD_KEY_INSRT_WRNG", "btree.py")
@mg.has_mutant("ECR_SELF_KEY_WRNG", "btree.py")
@mg.has_mutant("ECR_L_REMOVE_KEY_WRNG", "btree.py")
@mg.has_mutant("ECR_SELF_MERGE_CH_WRNG", "btree.py")
@mg.has_mutant("ECR_WRNG_RT_1", "btree.py")
@mg.has_mutant("ECR_WRNG_RT_2", "btree.py")

# Function: merge_children

@mg.has_mutant("MG_GT_RPL_GTE", "btree.py")
@mg.has_mutant("MG_L_R_WRNG_ASSGN", "btree.py")
@mg.has_mutant("MG_SELF_CHN_WRNG_IND", "btree.py")

# Function: remove_max

@mg.has_mutant("RMAX_KEYS_LEN_PLUS_1", "btree.py")
@mg.has_mutant("RMAX_CH_LEN_PLUS_1", "btree.py")


class BTreeSet:

    # The degree is the minimum number of children each non-root internal node must have.
    def __init__(self, degree, coll=None):
        if not isinstance(degree, int):
            raise TypeError()
        if degree < 2:
            raise ValueError("Degree must be at least 2")
        self.minkeys = degree - 1  # At least 1, equal to degree-1
        self.maxkeys = degree * 2 - 1  # At least 3, odd number, equal to minkeys*2+1

        self.clear()
        if coll is not None:
            for obj in coll:
                self.add(obj)

    def __len__(self):
        return self.size

    def clear(self):
        self.root = BTreeSet.Node(self.maxkeys, True)
        self.size = mg.mut("CLEAR_NO_SIZE_UPDATE", lambda: 0, lambda: self.size)

    def contains(self, obj):
        return self.__contains__(obj)

    def __contains__(self, obj):
        # Walk down the tree
        node = self.root
        while True:
            found, index = node.search(obj)
            if found:
                return True
            elif node.is_leaf():
                return False
            else:  # Internal node
                node = node.children[index]

    def add(self, obj):
        # Special preprocessing to split root node
        root = self.root
        if len(root.keys) == self.maxkeys:
            child = mg.mut("ADD_NO_CHILD_UPDATE", lambda: root, lambda: child)
            self.root = root = BTreeSet.Node(self.maxkeys, False)  # Increment tree height
            root.children.append(child)
            root.split_child(self.minkeys, self.maxkeys, 0)

        # Walk down the tree
        node = root
        while True:
            # Search for index in current node
            assert len(node.keys) < self.maxkeys
            assert node is root or mg.mut("ADD_GT_RPL_GTE", lambda: len(node.keys) >= self.minkeys, lambda: len(node.keys) > self.minkeys)
            found, index = node.search(obj)
            if found:
                return  # Key already exists in tree

            if node.is_leaf():  # Simple insertion into leaf
                node.keys.insert(index, obj)
                self.size += mg.mut("ADD_NO_SIZE_UPDATE", lambda: 1, lambda: 0)
                return  # Successfully added

            else:  # Handle internal node
                child = node.children[index]
                if len(child.keys) == self.maxkeys:  # Split child node
                    node.split_child(self.minkeys, self.maxkeys, mg.mut("ADD_NO_SPLIT_INDEX", lambda: index, lambda: 0))
                    if obj == node.keys[index]:
                        return  # Key already exists in tree
                    elif mg.mut("ADD_GTE_RPL_GT", lambda: obj > node.keys[index], lambda: obj >= node.keys[index]):
                        child = node.children[mg.mut("ADD_CHILD_WRONG_UPDATE", lambda: index + 1, lambda: index)]
                node = child

    def remove(self, obj):
        if not self._remove(obj):
            raise KeyError(str(obj))

    def discard(self, obj):
        self._remove(obj)

    # Returns whether an object was removed.
    def _remove(self, obj):
        # Walk down the tree
        root = self.root
        found, index = root.search(obj)
        node = root
        while True:
            assert mg.mut("REMOVE_GT_RPL_GTE",
                          lambda: len(node.keys) <= self.maxkeys,
                          lambda: len(node.keys) < self.maxkeys
                          )
            assert node is root or len(node.keys) > self.minkeys
            if node.is_leaf():
                if found:  # Simple removal from leaf
                    node.remove_key(index)
                    assert mg.mut("REMOVE_NO_SIZE_CHECK", lambda: self.size > 0, lambda: True)
                    self.size -= 1
                return found

            else:  # Internal node
                if found:  # Key is stored at current node
                    left, right = node.children[index: mg.mut("REMOVE_LR_WRONG_ASSGN",
                                                              lambda: index + 2,
                                                              lambda: index+1
                                                              )]
                    if len(left.keys) > self.minkeys:  # Replace key with predecessor
                        node.keys[index] = left.remove_max(self.minkeys)
                        assert self.size > 0
                        self.size -= mg.mut("REMOVE_NO_SIZE_UPDATE", lambda: 1, lambda: 0)
                        return True
                    elif len(right.keys) > self.minkeys:
                        node.keys[index] = right.remove_min(self.minkeys)
                        assert self.size > 0
                        self.size -= mg.mut("REMOVE_NO_SIZE_UPDATE", lambda: 1, lambda: 0)
                        return True
                    else:  # Merge key and right node into left node, then recurse
                        node.merge_children(self.minkeys, index)
                        if mg.mut("REMOVE_NO_NODE_ROOT_CMP", lambda: node is root, lambda: True) and len(root.keys) == 0:
                            assert len(root.children) == 1
                            self.root = root = mg.mut("REMOVE_FLIP_DEC_HEIGHT", lambda: left, lambda: right)  # Decrement tree height
                        node = left
                        index = mg.mut("REMOVE_NO_INDEX_UPDATE", lambda: self.minkeys, lambda: index)  # Index known due to merging; no need to search

                else:  # Key might be found in some child
                    child = node.ensure_child_remove(self.minkeys, index)
                    if node is root and len(root.keys) == 0:
                        assert len(root.children) == 1
                        self.root = root = root.children[0]  # Decrement tree height
                    node = child
                    found, index = node.search(obj)

    # Note: Not fail-fast on concurrent modification.
    def __iter__(self):
        # Initialization
        stack = []

        def push_left_path(node):
            while True:
                stack.append((node, 0))
                if node.is_leaf():
                    break
                node = node.children[0]

        push_left_path(self.root)

        # Generate elements
        while len(stack) > 0:
            node, index = stack.pop()
            if node.is_leaf():
                assert index == 0
                yield from node.keys
            else:
                yield node.keys[index]
                index += 1
                if index < len(node.keys):
                    stack.append((node, index))
                push_left_path(node.children[index])

    # For unit tests
    def check_structure(self):
        # Check size and root node properties
        size = self.size
        root = self.root
        if not isinstance(root, BTreeSet.Node) or size < 0 or (size > self.maxkeys and root.is_leaf()) \
                or (size <= self.minkeys * 2 and (not root.is_leaf() or len(root.keys) != size)):
            raise AssertionError("Invalid size or root type")

        # Calculate height by descending into one branch
        height = 0
        node = root
        while not node.is_leaf():
            height += 1
            node = node.children[0]

        # Check all nodes and total size
        if root.check_structure(self.minkeys, self.maxkeys, True, height, None, None) != size:
            raise AssertionError("Size mismatch")

    # ---- Helper class ----

    class Node:

        # -- Constructor --

        # Note: Once created, a node's structure never changes between a leaf and internal node.
        def __init__(self, maxkeys, leaf):
            assert mg.mut("NODE_INIT_GT_RPL_GTE", lambda: maxkeys >= 3, lambda: maxkeys > 3) and maxkeys % 2 == 1
            self.keys = []  # Length is in [0, maxkeys] for root node, [minkeys, maxkeys] for all other nodes
            self.children = None if leaf else []  # If internal node, then length always equals len(keys)+1

        # -- Methods for getting info --

        def is_leaf(self):
            return self.children is None

        # Searches this node's keys list and returns (True, i) if obj equals keys[i],
        # otherwise returns (False, i) if children[i] should be explored. For simplicity,
        # the implementation uses linear search. It's possible to replace it with binary search for speed.
        def search(self, obj):
            keys = self.keys
            i = 0
            while mg.mut("NODE_SEARCH_GTE_RPL_GT_1", lambda: i < len(keys), lambda: i <= len(keys)):
                if obj == keys[i]:
                    assert mg.mut("NODE_SEARCH_GT_RPL_GTE", lambda: 0 <= i < len(keys), lambda: 0 < i < len(keys))
                    return (True, i)  # Key found
                elif mg.mut("NODE_SEARCH_GTE_RPL_GT_2", lambda: obj > keys[i], lambda: obj >= keys[i]):
                    i += 1
                else:
                    break
            assert mg.mut("NODE_SEARCH_LT_RPL_LTE", lambda: 0 <= i <= len(keys), lambda: 0 <= i < len(keys))
            return (False, i)  # Not found, caller should recurse on child

        # -- Methods for insertion --

        # For the child node at the given index, this moves the right half of keys and children to a new node,
        # and adds the middle key and new child to this node. The left half of child's data is not moved.
        def split_child(self, minkeys, maxkeys, index):
            assert not self.is_leaf() and 0 <= index <= len(self.keys) < maxkeys
            left = self.children[index]
            assert len(left.keys) == maxkeys
            right = BTreeSet.Node(maxkeys, left.is_leaf())
            self.children.insert(mg.mut("NODE_SPLT_CH_CHILD_INSERT_WRNG", lambda: index + 1, lambda: index), right)

            # Handle children
            if not left.is_leaf():
                right.children.extend(left.children[mg.mut("NODE_SPLT_CH_R_CH_EXT_WRNG", lambda: minkeys + 1, lambda: minkeys) :])
                del left.children[mg.mut("NODE_SPLT_CH_L_CH_EXT_WRNG", lambda: minkeys + 1, lambda: minkeys) :]

            # Handle keys
            self.keys.insert(index, left.keys[minkeys])
            right.keys.extend(left.keys[mg.mut("NODE_SPLT_CH_R_KEYS_EXT_WRNG", lambda: minkeys + 1, lambda: minkeys) :])
            del left.keys[minkeys:]

        # -- Methods for removal --

        # Performs modifications to ensure that this node's child at the given index has at least
        # minKeys+1 keys in preparation for a single removal. The child may gain a key and subchild
        # from its sibling, or it may be merged with a sibling, or nothing needs to be done.
        # A reference to the appropriate child is returned, which is helpful if the old child no longer exists.
        def ensure_child_remove(self, minkeys, index):
            # Preliminaries
            assert not self.is_leaf() and mg.mut("ECR_GT_RPL_GTE_1", lambda: 0 <= index < len(self.children), lambda: 0 < index < len(self.children))
            child = self.children[index]
            if mg.mut("ECR_GTE_RPL_GT_1", lambda: len(child.keys) > minkeys, lambda: len(child.keys) >= minkeys) :  # Already satisfies the condition
                return child
            assert len(child.keys) == minkeys

            # Get siblings
            left = self.children[mg.mut("ECR_L_SBLNG_WRNG", lambda: index - 1, lambda: index)] if mg.mut("ECR_GT_RPL_GTE_2", lambda: index >= 1, lambda: index > 1) else None
            right = self.children[mg.mut("ECR_R_SBLNG_WRNG", lambda: index + 1, lambda: index)] if mg.mut("ECR_GTE_RPL_GT_2", lambda: index < len(self.keys), lambda:index <= len(self.keys))  else None
            internal = not child.is_leaf()
            assert left is not None or right is not None  # At least one sibling exists because degree >= 2
            assert left is None or left.is_leaf() != internal  # Sibling must be same type (internal/leaf) as child
            assert right is None or right.is_leaf() != internal  # Sibling must be same type (internal/leaf) as child

            if left is not None and len(left.keys) > minkeys:  # Steal rightmost item from left sibling
                if internal:
                    child.children.insert(0, left.children.pop(-1))
                child.keys.insert(0, self.keys[mg.mut("ECR_CHLD_KEY_INSRT_WRNG", lambda: index - 1, lambda: index)])
                self.keys[mg.mut("ECR_SELF_KEY_WRNG", lambda: index - 1, lambda: index)] = left.remove_key(len(left.keys) - mg.mut("ECR_L_REMOVE_KEY_WRNG", lambda: 1, lambda: 0))
                return child
            elif right is not None and len(right.keys) > minkeys:  # Steal leftmost item from right sibling
                if internal:
                    child.children.append(right.children.pop(0))
                child.keys.append(self.keys[index])
                self.keys[index] = right.remove_key(0)
                return child
            elif left is not None:  # Merge child into left sibling
                self.merge_children(minkeys, index - mg.mut("ECR_SELF_MERGE_CH_WRNG", lambda: 1, lambda: 0))
                return mg.mut("ECR_WRNG_RT_2", lambda: left, lambda: child)  # This is the only case where the return value is different
            elif right is not None:  # Merge right sibling into child
                self.merge_children(minkeys, index)
                return mg.mut("ECR_WRNG_RT_1", lambda: child, lambda: right)
            else:
                raise AssertionError("Impossible condition")

        # Merges the child node at index+1 into the child node at index,
        # assuming the current node is not empty and both children have minkeys.
        def merge_children(self, minkeys, index):
            assert not self.is_leaf() and mg.mut("MG_GT_RPL_GTE", lambda: 0 <= index < len(self.keys), lambda: 0 < index < len(self.keys))
            left, right = self.children[index: mg.mut("MG_L_R_WRNG_ASSGN", lambda: index + 2, lambda: index + 1)]
            assert len(left.keys) == len(right.keys) == minkeys
            if not left.is_leaf():
                left.children.extend(right.children)
            del self.children[mg.mut("MG_SELF_CHN_WRNG_IND", lambda: index + 1, lambda: index)]
            left.keys.append(self.remove_key(index))
            left.keys.extend(right.keys)

        # Removes and returns the minimum key among the whole subtree rooted at this node.
        # Requires this node to be preprocessed to have at least minkeys+1 keys.
        def remove_min(self, minkeys):
            node = self
            while True:
                assert len(node.keys) > minkeys
                if node.is_leaf():
                    return node.remove_key(0)
                else:
                    node = node.ensure_child_remove(minkeys, 0)

        # Removes and returns the maximum key among the whole subtree rooted at this node.
        # Requires this node to be preprocessed to have at least minkeys+1 keys.
        def remove_max(self, minkeys):
            node = self
            while True:
                assert len(node.keys) > minkeys
                if node.is_leaf():
                    return node.remove_key(len(node.keys) - mg.mut("RMAX_KEYS_LEN_PLUS_1", lambda: 1, lambda: 0))
                else:
                    node = node.ensure_child_remove(minkeys, len(node.children) - mg.mut("RMAX_CH_LEN_PLUS_1", lambda: 1, lambda: 0))

        # Removes and returns this node's key at the given index.
        def remove_key(self, index):
            assert 0 <= index < len(self.keys)
            return self.keys.pop(index)

        # -- Miscellaneous methods --

        # Checks the structure recursively and returns the total number
        # of keys in the subtree rooted at this node. For unit tests.
        def check_structure(self, minkeys, maxkeys, isroot, leafdepth, min, max):
            # Check basic fields
            keys = self.keys
            numkeys = len(keys)
            if self.is_leaf() != (leafdepth == 0):
                raise AssertionError("Incorrect leaf/internal node type")
            if numkeys > maxkeys:
                raise AssertionError("Invalid number of keys")
            if isroot and not self.is_leaf() and numkeys == 0:
                raise AssertionError("Invalid number of keys")
            if not isroot and numkeys < minkeys:
                raise AssertionError("Invalid number of keys")

            # Check keys for strict increasing order
            tempkeys = [min] + keys + [max]
            for i in range(len(tempkeys) - 1):
                x = tempkeys[i]
                y = tempkeys[i + 1]
                if x is not None and y is not None and y <= x:
                    raise AssertionError("Invalid key ordering")

            # Check children recursively and count keys in this subtree
            count = numkeys
            if not self.is_leaf():
                if len(self.children) != numkeys + 1:
                    raise AssertionError("Invalid number of children")
                for (i, child) in enumerate(self.children):
                    # Check children pointers and recurse
                    if not isinstance(child, BTreeSet.Node):
                        raise TypeError()
                    count += child.check_structure(minkeys, maxkeys, False,
                                                   leafdepth - 1, tempkeys[i], tempkeys[i + 1])
            return count

testing_strategy = st.lists(st.integers(), unique=True)
def testing_function(lst):
    flag = True

    to_delete = lst[0:int(len(lst) / 2)]
    # print(to_delete)

    try:

        tree = BTreeSet(2)

        for i in lst:
            tree.add(i)

        for i in to_delete:
            tree.remove(i)
            lst.remove(i)

        for i in lst:
            if not tree.contains(i):
                flag = False

        for i in to_delete:
            if tree.contains(i):
                flag = False
    except:
        flag = False

    # print(flag)
    assert flag
