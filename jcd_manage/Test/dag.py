from jcd_manage.Config.types import DAGBoolType
from jcd_manage.Data.dag import PrimitiveSurface, SurfaceGroup, BooleanOp, CSGDAG


def test():
    dag = CSGDAG()

    # primitive surfaces
    A = dag.add(PrimitiveSurface(surface_data="plane"))
    B = dag.add(PrimitiveSurface(surface_data="nurbs_Surface"))
    C = dag.add(PrimitiveSurface(surface_data="cylinder"))
    D = dag.add(PrimitiveSurface(surface_data="sphere"))

    # group
    G1 = dag.add(SurfaceGroup([A, B]))

    # Boolean ops
    X = dag.add(BooleanOp(DAGBoolType.UNION, G1, C))      # X = G1 ∪ C
    Y = dag.add(BooleanOp(DAGBoolType.DIFFERENCE, X, D))  # Y = X - D

    # print structure
    dag.print_tree(Y)
    return True
