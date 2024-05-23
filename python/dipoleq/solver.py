"""
Forward solve the dipole equilibrium
This is the same as SimDipEq, but in python
"""

from .core import Machine


def do_free_boundary(m: Machine, makeFit: bool = False, isFirst: bool = True):
    """do the free boundary solution for the grad-shafranov equation
    with a single iteration of solving the fixed boundary solution
    and then determining the plasma boundary and then updating the
    plasma current
    """

    pg = m.PsiGrid

    if m.NumShells > 0:
        m.find_shell_current()

    if isFirst:
        m.load_bndry_greens()

    m.psi_boundary()
    m.add_coil_J()
    m.add_shell_J()
    pg.go_PDE()
    m.find_plasma_boundary()

    if makeFit:
        if isFirst:
            m.load_meas_greens()
        m.least_squares(1 if isFirst else 0)

    if m.VacuumOnly:
        m.zero_J()
    else:
        m.find_J()


def do_fixed_boundary(m: Machine, makeFit: bool = False):
    """do the fixed boundary solution for the grad-shafranov equation
    assume the edge is fixed
    (not sure about the effect of the shells in this case)
    """

    pg = m.PsiGrid
    m.add_coil_J()
    m.add_shell_J()
    pg.go_PDE()
    m.find_plasma_boundary()
    if makeFit:
        m.least_squares(0)
    if m.VacuumOnly:
        m.zero_J()
    else:
        m.find_J()


def iterate_solution(m: Machine, makeFit: bool = False):
    """Iterate free_boundary and then some fixed_boundaries
    to find the overall solution when the boundary error is
    below the threshold
    """
    for ifree in range(1, m.MaxIterFree + 1):
        do_free_boundary(m, makeFit=makeFit, isFirst=(ifree == 1))
        for ifixed in range(1, m.MaxIterFixed + 1):
            do_fixed_boundary(m)
            m.IterFixed = ifixed
        m.IterFree = ifree
        pg = m.PsiGrid
        if (ifree > 1) and (pg.BoundError < pg.BoundThreshold):
            m.free_bndry_greens()
            m.free_meas_greens()
            break


def solve(m: Machine):
    """Solve the Grad-Shafranov equation for the machine m

    Args:
        m (Machine): Complete machine object with all the necessary
            parameters set.
    """
    m.set_start_time()

    # don't use restart files, this isn't 1993
    # if m.RestartStatus == 1:
    #    m.read_restart()
    # else:

    m.PsiGrid.init_J(m.Plasma)

    iterate_solution(m)

    # m.write_restart()

    m.get_plasma_parameters()
    m.set_stop_time()