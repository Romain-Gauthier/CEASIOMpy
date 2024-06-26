"""
CEASIOMpy: Conceptual Aircraft Design Software

Developed by CFS ENGINEERING, 1015 Lausanne, Switzerland

Test functions from 'lib/utils/mathfunctions.py'

Python version: >=3.8

| Author : Aidan Jungo
| Creation: 2018-10-19

"""

# =================================================================================================
#   IMPORTS
# =================================================================================================

from ceasiompy.utils.ceasiomlogger import get_logger
from ceasiompy.utils.generalclasses import SimpleNamespace
from ceasiompy.utils.mathfunctions import euler2fix, fix2euler
from pytest import approx

log = get_logger()

# =================================================================================================
#   CLASSES
# =================================================================================================


# =================================================================================================
#   FUNCTIONS
# =================================================================================================


def test_euler2fix():
    """Test convertion from Euler angles to fix angles"""

    euler_angle = SimpleNamespace()

    euler_angle.x = 0
    euler_angle.y = 0
    euler_angle.z = 0
    fix_angle = euler2fix(euler_angle)
    assert fix_angle.x == 0.0
    assert fix_angle.y == 0.0
    assert fix_angle.z == 0.0

    euler_angle.x = 50
    euler_angle.y = 32
    euler_angle.z = 65
    fix_angle = euler2fix(euler_angle)
    assert fix_angle.x == approx(49.24)
    assert fix_angle.y == approx(-33.39)
    assert fix_angle.z == approx(64.58)

    euler_angle.x = -12.5
    euler_angle.y = 27
    euler_angle.z = 93
    fix_angle = euler2fix(euler_angle)
    assert fix_angle.x == approx(27.56)
    assert fix_angle.y == approx(11.12)
    assert fix_angle.z == approx(92.72)

    euler_angle.x = 90
    euler_angle.y = 90
    euler_angle.z = 90
    fix_angle = euler2fix(euler_angle)
    assert fix_angle.x == 90.0
    assert fix_angle.y == -90.0
    assert fix_angle.z == 90.0


def test_fix2euler():
    """Test convertion from fix angles to Euler angles"""

    fix_angle = SimpleNamespace()

    fix_angle.x = 0
    fix_angle.y = 0
    fix_angle.z = 0
    euler_angle = euler2fix(fix_angle)
    assert euler_angle.x == 0.0
    assert euler_angle.y == 0.0
    assert euler_angle.z == 0.0

    fix_angle.x = 90
    fix_angle.y = 90
    fix_angle.z = 90
    euler_angle = euler2fix(fix_angle)
    assert euler_angle.x == 90.0
    assert euler_angle.y == -90.0
    assert euler_angle.z == 90.0

    # Test by doing both transformation
    fix_angle.x = 30.23
    fix_angle.y = -85.52
    fix_angle.z = -10.98
    euler_angle = fix2euler(fix_angle)
    fix_angle2 = euler2fix(euler_angle)
    assert fix_angle == fix_angle2


# =================================================================================================
#    MAIN
# =================================================================================================

if __name__ == "__main__":

    log.info("Running Test Math Functions")
    log.info("To run test use the following command:")
    log.info(">> pytest -v")
