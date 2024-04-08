from typing import Any, List, Optional, Set


class BinaryTree:
    _root: Any
    _child: List['BinaryTree']

    def __init__(self, root: Any):
        self._root = root
        self._child = []

    def insert(self, value: Any) -> 'BinaryTree':
        if isinstance(value, BinaryTree):
            self._child.append(value)
        else:
            self._child.append(BinaryTree(value))
        return self

    @property
    def is_leaf(self) -> bool:
        return len(self._child) == 0

    @property
    def children(self) -> List['BinaryTree']:
        return self._child

    @property
    def root(self) -> Any:
        return self._root

    def __repr__(self) -> str:
        if self.is_leaf:
            return f"BinaryTree({self._root})"
        return f"BinaryTree(root={self._root}, children={self._child})"

    def __str__(self) -> str:
        return self.get_tree(self)

    def search(self, value: Any, res: List['BinaryTree']) -> bool:
        res.append(self)
        if isinstance(value, BinaryTree):
            if self == value:
                return True
        else:
            if self._root == value:
                return True
        for child in self._child:
            if child.search(value, res):
                return True
        res.remove(self)
        return False

    @staticmethod
    def get_tree(node: 'BinaryTree', prefix: List[str] = (), depth: int = 0, hide: Optional[Set[int]] = None) -> str:
        if hide is None:
            hide = set()
        res = f"{''.join(prefix)}{node._root}\n"
        if not node.is_leaf:
            for i, child in enumerate(node._child):
                prefix = ['│\t'] * depth
                for j in hide:
                    prefix[j] = '\t'
                if i == len(node._child) - 1:
                    prefix.append('└─')
                    hide.add(depth)
                else:
                    prefix.append('├─')
                res += node.get_tree(child, prefix, depth + 1, hide)
                if depth in hide:
                    hide.remove(depth)
        return res
