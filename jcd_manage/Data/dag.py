from jcd_manage.Config.types import DAGNodeType, DAGBoolType

# ---------------------------------------------------------
# Base Node Class
# ---------------------------------------------------------

class Node:
    _id_counter = 0

    def __init__(self, node_type: DAGNodeType):
        self.id = Node._id_counter
        Node._id_counter += 1

        self.type = node_type
        self.children = []         # dependency nodes
        self.cached_result = None  # place to store computed B-Rep or mesh

    def __repr__(self):
        return f"<Node {self.id} type={self.type}>"


# ---------------------------------------------------------
# Primitive
# ---------------------------------------------------------

class PrimitiveSurface(Node):
    def __init__(self, surface_data):
        super().__init__(DAGNodeType.PRIMITIVE)
        self.surface_data = surface_data  # raw NURBS / B-spline / parametric data

    def __repr__(self):
        return f"<PrimitiveSurface id={self.id}>"


# ---------------------------------------------------------
# Group of surfaces (treated as one body)
# ---------------------------------------------------------

class SurfaceGroup(Node):
    def __init__(self, items):
        super().__init__(DAGNodeType.GROUP)
        self.items = items  # list of Node ids
        self.children.extend(items)

    def __repr__(self):
        return f"<SurfaceGroup id={self.id} items={self.items}>"


# ---------------------------------------------------------
# Boolean Operation Node
# ---------------------------------------------------------

class BooleanOp(Node):
    def __init__(self, op: DAGBoolType, left_id: int, right_id: int):
        super().__init__(DAGNodeType.BOOLEAN)

        self.op = op
        self.left = left_id
        self.right = right_id

        self.children.extend([left_id, right_id])

    def __repr__(self):
        return f"<BooleanOp id={self.id} op={self.op.value} ({self.left}, {self.right})>"


# ---------------------------------------------------------
# DAG Manager
# ---------------------------------------------------------

class CSGDAG:
    def __init__(self):
        self.nodes = {}  # id -> node

    def add(self, node: Node):
        self.nodes[node.id] = node
        return node.id

    def get(self, node_id):
        return self.nodes[node_id]

    # recursively print dependency tree
    def print_tree(self, node_id, indent=0, visited=None):
        if visited is None:
            visited = set()
        if node_id in visited:
            print(" " * indent + f"{node_id} (revisited)")
            return
        visited.add(node_id)

        node = self.get(node_id)
        print(" " * indent + repr(node))

        for child in node.children:
            self.print_tree(child, indent + 4, visited)
