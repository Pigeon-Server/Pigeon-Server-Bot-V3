from typing import Generic, List, Optional, Set, TypeVar, Union

T = TypeVar('T')


class Tree(Generic[T]):
    _root: T
    _children: List['Tree']

    def __init__(self, root: T):
        self._root = root
        self._children = []

    def insert(self, value: Union[T, 'Tree']) -> 'Tree':
        if isinstance(value, Tree):
            self._children.append(value)
        else:
            self._children.append(Tree(value))
        return self

    @property
    def is_leaf(self) -> bool:
        return len(self._children) == 0

    @property
    def children(self) -> List['Tree']:
        return self._children

    @property
    def root(self) -> T:
        return self._root

    def __repr__(self) -> str:
        if self.is_leaf:
            return f"BinaryTree({self._root})"
        return f"BinaryTree(root={self._root}, children={self._children})"

    def __str__(self) -> str:
        return self.get_tree(self)

    def search(self, value: Union[T, 'Tree'], res: Optional[List['Tree']] = None) -> bool:
        if res is not None:
            res.append(self)
        if isinstance(value, Tree) and self.root == value.root:
            return True
        else:
            if self._root == value:
                return True
        for child in self._children:
            if child.search(value, res):
                return True
        if res is not None:
            res.remove(self)
        return False

    def get_node(self, path_list: list[T], *, match_most: bool = False) -> Optional['Tree']:
        current_node = self
        length = 0
        for value in path_list:
            child_found = False
            for child in current_node.children:
                if child.root == value:
                    current_node = child
                    child_found = True
                    break
            if not child_found:
                if match_most:
                    return self.get_node(path_list[:length])
                return None
            length += 1

        return current_node

    @staticmethod
    def get_tree(node: 'Tree', prefix: List[str] = (), depth: int = 0, hide: Optional[Set[int]] = None) -> str:
        if hide is None:
            hide = set()
        res = f"{''.join(prefix)}{node._root}\n"
        if not node.is_leaf:
            for i, child in enumerate(node._children):
                prefix = ['│\t'] * depth
                for j in hide:
                    prefix[j] = '\t'
                if i == len(node._children) - 1:
                    prefix.append('└─')
                    hide.add(depth)
                else:
                    prefix.append('├─')
                res += node.get_tree(child, prefix, depth + 1, hide)
                if depth in hide:
                    hide.remove(depth)
        return res
