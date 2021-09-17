# Code from https://github.com/bfaure/Python3_Data_Structures/blob/master/AVL_Tree/main.py

from hypothesis import example, Phase, settings, Verbosity, given, strategies as st, HealthCheck
import json
import random


# mutants for insert

@mg.has_mutant("INSERT_PARENT_NOT_UPDATED", "AVLTree.py")
@mg.has_mutant("INSERT_NO_NULL_CHECK", "AVLTree.py")
# mutants for search

@mg.has_mutant("SEARCH_NO_NULL_CHECK", "AVLTree.py")
# mutants for delete

@mg.has_mutant("DELETE_NODE_CHILDREN_PLUS_1", "AVLTree.py")
@mg.has_mutant("DELETE_CASE_2_NO_PARENT_UPDATE", "AVLTree.py")
@mg.has_mutant("DELETE_CASE_3_FLIP_SUCCESSOR", "AVLTree.py")
@mg.has_mutant("DELETE_FLIP_MIN_VALUE", "AVLTree.py")
@mg.has_mutant("DELETE_HEIGHT_MINUS_1", "AVLTree.py")
# Other functions

@mg.has_mutant("ROTATE_RIGHT_Z_HEIGHT_MINUS_1", "AVLTree.py")
@mg.has_mutant("ROTATE_LEFT_Y_HEIGHT_MINUS_1", "AVLTree.py")
@mg.has_mutant("ROTATE_LEFT_NO_PARENT_UPDATE", "AVLTree.py")
@mg.has_mutant("INSPECT_INSERTION_HEIGHT_MINUS_1", "AVLTree.py")
@mg.has_mutant("REBALANCE_FLIP_MUTANT_1", "AVLTree.py")
@mg.has_mutant("REBALANCE_FLIP_MUTANT_2", "AVLTree.py")
@mg.has_mutant("INSPECT_DELETE_NO_ABS", "AVLTree.py")
@mg.has_mutant("INSPECT_DELETE_FLIP_ARGS", "AVLTree.py")

class Node:
    def __init__(self, value=None):
        self.value = value
        self.left_child = None
        self.right_child = None
        self.parent = None  # pointer to parent node in tree
        self.height = 1  # height of node in tree (max dist. to leaf) NEW FOR AVL

    def __repr__(self):
        if self.value is None: return 'None'
        return "Node \nValue:" + str(self.value)


class AVLTree:
    def __init__(self):
        self.root = None

    def __repr__(self):
        if self.root is None: return ''
        content = '\n'  # to hold final string
        cur_nodes = [self.root]  # all nodes at current level
        cur_height = self.root.height  # height of nodes at current level
        sep = ' ' * (2 ** (cur_height - 1))  # variable sized separator between elements
        while True:
            cur_height += -1  # decrement current height
            if len(cur_nodes) == 0: break
            cur_row = ' '
            next_row = ''
            next_nodes = []

            if all(n is None for n in cur_nodes):
                break

            for n in cur_nodes:

                if n is None:
                    cur_row += '   ' + sep
                    next_row += '   ' + sep
                    next_nodes.extend([None, None])
                    continue

                if n.value is not None:
                    buf = ' ' * int((5 - len(str(n.value))) / 2)
                    cur_row += '%s%s%s' % (buf, str(n.value), buf) + sep
                else:
                    cur_row += ' ' * 5 + sep

                if n.left_child is not None:
                    next_nodes.append(n.left_child)
                    next_row += ' /' + sep
                else:
                    next_row += '  ' + sep
                    next_nodes.append(None)

                if n.right_child is not None:
                    next_nodes.append(n.right_child)
                    next_row += '\n' + sep
                else:
                    next_row += '  ' + sep
                    next_nodes.append(None)

            content += (cur_height * '   ' + cur_row + '\n' + cur_height * '   ' + next_row + '\n')
            cur_nodes = next_nodes
            sep = ' ' * int(len(sep) / 2)  # cut separator size in half
        return content


    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert(value, self.root)

    def _insert(self, value, cur_node):
        if value < cur_node.value:
            if mg.mut("INSERT_NO_NULL_CHECK", lambda: cur_node.left_child is None, lambda: True):
                cur_node.left_child = Node(value)
                cur_node.left_child.parent = mg.mut("INSERT_PARENT_NOT_UPDATED", lambda: cur_node, lambda: cur_node.left_child.parent) # set parent
                self._inspect_insertion(cur_node.left_child)
            else:
                self._insert(value, cur_node.left_child)
        elif value > cur_node.value:
            if mg.mut("INSERT_NO_NULL_CHECK", lambda: cur_node.right_child is None, lambda: True):
                cur_node.right_child = Node(value)
                cur_node.right_child.parent = mg.mut("INSERT_PARENT_NOT_UPDATED", lambda: cur_node, lambda: cur_node.right_child.parent) # set parent
                self._inspect_insertion(cur_node.right_child)
            else:
                self._insert(value, cur_node.right_child)


    def print_tree(self):
        if self.root is not None:
            self._print_tree(self.root)

    def _print_tree(self, cur_node):
        if cur_node is not None:
            self._print_tree(cur_node.left_child)
            print('%s, h=%d' % (str(cur_node.value), cur_node.height))
            self._print_tree(cur_node.right_child)

    def height(self):
        if self.root is not None:
            return self._height(self.root, 0)
        else:
            return 0

    def _height(self, cur_node, cur_height):
        if cur_node is None: return cur_height
        left_height = self._height(cur_node.left_child, cur_height + 1)
        right_height = self._height(cur_node.right_child, cur_height + 1)
        return max(left_height, right_height)

    def find(self, value):
        if self.root is not None:
            return self._find(value, self.root)
        else:
            return None

    def _find(self, value, cur_node):
        if value == cur_node.value:
            return cur_node
        elif value < cur_node.value and cur_node.left_child is not None:
            return self._find(value, cur_node.left_child)
        elif value > cur_node.value and cur_node.right_child is not None:
            return self._find(value, cur_node.right_child)

    def delete_value(self, value):
        return self.delete_node(self.find(value))

    def delete_node(self, node):

        ## -----
        # Improvements since prior lesson

        # Protect against deleting a node not found in the tree
        if node is None or self.find(node.value) is None:
            print("Node to be deleted not found in the tree!")
            return None

        ## -----

        # returns the node with min value in tree rooted at input node
        def min_value_node(n):
            current = n
            while mg.mut("DELETE_FLIP_MIN_VALUE", lambda: current.left_child, lambda: current.right_child) is not None:
                current = mg.mut("DELETE_FLIP_MIN_VALUE", lambda: current.left_child, lambda: current.right_child)
            return current

        # returns the number of children for the specified node
        def num_children(n):
            num_children = 0
            if n.left_child is not None: num_children += 1
            if n.right_child is not None: num_children += 1
            return num_children

        # get the parent of the node to be deleted
        node_parent = node.parent

        # get the number of children of the node to be deleted
        node_children = mg.mut("DELETE_NODE_CHILDREN_PLUS_1", lambda: num_children(node), lambda: num_children(node) + 1)

        # break operation into different cases based on the
        # structure of the tree & node to be deleted

        # CASE 1 (node has no children)
        if node_children == 0:

            if node_parent is not None:
                # remove reference to the node from the parent
                if node_parent.left_child == node:
                    node_parent.left_child = None
                else:
                    node_parent.right_child = None
            else:
                self.root = None

        # CASE 2 (node has a single child)
        if node_children == 1:

            # get the single child node
            if node.left_child is not None:
                child = node.left_child
            else:
                child = node.right_child

            if node_parent is not None:
                # replace the node to be deleted with its child
                if node_parent.left_child == node:
                    node_parent.left_child = child
                else:
                    node_parent.right_child = child
            else:
                self.root = child

            # correct the parent pointer in node
            child.parent = mg.mut("DELETE_CASE_2_NO_PARENT_UPDATE", lambda: node_parent, lambda: child.parent)

        # CASE 3 (node has two children)
        if node_children == 2:
            # get the inorder successor of the deleted node
            successor = min_value_node(mg.mut("DELETE_CASE_3_FLIP_SUCCESSOR", lambda: node.right_child, lambda: node.left_child))

            # copy the inorder successor's value to the node formerly
            # holding the value we wished to delete
            node.value = successor.value

            # delete the inorder successor now that it's value was
            # copied into the other node
            self.delete_node(successor)

            # exit function so we don't call the _inspect_deletion twice
            return

        if node_parent is not None:
            # fix the height of the parent of current node
            node_parent.height = mg.mut("DELETE_HEIGHT_MINUS_1", lambda: 1, lambda: 0) + max(self.get_height(node_parent.left_child),
                                         self.get_height(node_parent.right_child))

            # begin to traverse back up the tree checking if there are
            # any sections which now invalidate the AVL balance rules
            self._inspect_deletion(node_parent)

    def search(self, value):
        if self.root is not None:
            return self._search(value, self.root)
        else:
            return False

    def _search(self, value, cur_node):
        if value == cur_node.value:
            return True
        elif mg.mut("SEARCH_NO_NULL_CHECK", lambda: value < cur_node.value and cur_node.left_child is not None, lambda: value < cur_node.value):
            return self._search(value, cur_node.left_child)
        elif mg.mut("SEARCH_NO_NULL_CHECK", lambda: value > cur_node.value and cur_node.right_child is not None, lambda: value > cur_node.value):
            return self._search(value, cur_node.right_child)
        return False

    # Functions added for AVL...

    def _inspect_insertion(self, cur_node, path=[]):
        if cur_node.parent is None: return
        path = [cur_node] + path

        left_height = self.get_height(cur_node.parent.left_child)
        right_height = self.get_height(cur_node.parent.right_child)

        if abs(left_height - right_height) > 1:
            path = [cur_node.parent] + path
            self._rebalance_node(path[0], path[1], path[2])
            return

        new_height = mg.mut("INSPECT_INSERTION_HEIGHT_MINUS_1", lambda: 1, lambda: 0) + cur_node.height
        if new_height > cur_node.parent.height:
            cur_node.parent.height = new_height

        self._inspect_insertion(cur_node.parent, path)

    def _inspect_deletion(self, cur_node):
        if cur_node is None: return

        left_height = self.get_height(cur_node.left_child)
        right_height = self.get_height(cur_node.right_child)

        if mg.mut("INSPECT_DELETE_NO_ABS", lambda: abs(left_height - right_height), lambda: left_height - right_height)  > 1:
            y = self.taller_child(cur_node)
            x = self.taller_child(y)
            self._rebalance_node(cur_node,
                                 mg.mut("INSPECT_DELETE_FLIP_ARGS", lambda: y, lambda: x),
                                 mg.mut("INSPECT_DELETE_FLIP_ARGS", lambda: x, lambda: y)
                                 )

        self._inspect_deletion(cur_node.parent)

    def _rebalance_node(self, z, y, x):
        if y == z.left_child and x == y.left_child:
            self._right_rotate(z)
        elif y == z.left_child and x == y.right_child:
            self._left_rotate(mg.mut("REBALANCE_FLIP_MUTANT_1", lambda: y, lambda: z))
            self._right_rotate(mg.mut("REBALANCE_FLIP_MUTANT_1", lambda: z, lambda: y))
        elif y == z.right_child and x == y.right_child:
            self._left_rotate(z)
        elif y == z.right_child and x == y.left_child:
            self._right_rotate(mg.mut("REBALANCE_FLIP_MUTANT_2", lambda: y, lambda: z))
            self._left_rotate(mg.mut("REBALANCE_FLIP_MUTANT_2", lambda: z, lambda: y))
        else:
            raise Exception('_rebalance_node: z,y,x node configuration not recognized!')

    def _right_rotate(self, z):
        sub_root = z.parent
        y = z.left_child
        t3 = y.right_child
        y.right_child = z
        z.parent = y
        z.left_child = t3
        if t3 is not None: t3.parent = z
        y.parent = sub_root
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left_child == z:
                y.parent.left_child = y
            else:
                y.parent.right_child = y
        z.height = mg.mut("ROTATE_RIGHT_Z_HEIGHT_MINUS_1", lambda: 1, lambda: 0) + max(self.get_height(z.left_child),
                           self.get_height(z.right_child))
        y.height = 1 + max(self.get_height(y.left_child),
                           self.get_height(y.right_child))

    def _left_rotate(self, z):
        sub_root = z.parent
        y = z.right_child
        t2 = y.left_child
        y.left_child = z
        z.parent = mg.mut("ROTATE_LEFT_NO_PARENT_UPDATE", lambda: y, lambda: z.parent)
        z.right_child = t2
        if t2 is not None: t2.parent = z
        y.parent = sub_root
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left_child == z:
                y.parent.left_child = y
            else:
                y.parent.right_child = y
        z.height = 1 + max(self.get_height(z.left_child),
                           self.get_height(z.right_child))
        y.height = mg.mut("ROTATE_LEFT_Y_HEIGHT_MINUS_1", lambda: 1, lambda: 0) + max(self.get_height(y.left_child),
                           self.get_height(y.right_child))

    def get_height(self, cur_node):
        if cur_node is None: return 0
        return cur_node.height

    def taller_child(self, cur_node):
        left = self.get_height(cur_node.left_child)
        right = self.get_height(cur_node.right_child)
        return cur_node.left_child if left >= right else cur_node.right_child

testing_strategy = st.lists(st.integers(), unique=True)
def testing_function(list):
    # print(list)
    flag = True
    # inconsistent results if random is used without fixed seed
    to_delete = list[0:int(len(list)/2)]
    # print(to_delete)

    try:

        tree = AVLTree()

        for i in list:
            tree.insert(i)

        for i in to_delete:
            tree.delete_value(i)
            list.remove(i)

        for i in list:
            if not tree.search(i):
                flag = False

        for i in to_delete:
            if tree.search(i):
                flag = False
    except:
        flag = False

    # print(flag)
    assert flag