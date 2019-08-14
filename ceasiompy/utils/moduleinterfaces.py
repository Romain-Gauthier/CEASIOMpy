"""
CEASIOMpy: Conceptual Aircraft Design Software

Developed for CFS ENGINEERING, 1015 Lausanne, Switzerland

Module interfaces functions to deal with CPACS input and output

Python version: >=3.6

| Author : Aaron Dettmann
| Creation: 2019-08-06
| Last modifiction: 2019-08-14

TODO:

    * Add somefunction for input/output files
"""

#==============================================================================
#   IMPORTS
#==============================================================================

from ceasiompy.utils.ceasiomlogger import get_logger
from ceasiompy.utils.cpacsfunctions import open_tixi, open_tigl, close_tixi

# Shortcut for XPath definition
CEASIOM_XPATH = '/cpacs/toolspecific/CEASIOMpy'
AIRCRAFT_XPATH = '/cpacs/vehicles/aircraft'


#==============================================================================
#   CLASSES
#==============================================================================

class CPACSRequirementError(Exception):
    pass


class _Entry:

    def __init__(self, *, var_name='', default_value=None, unit='1',
                 descr='', cpacs_path=''):
        """Template for an entry which describes a module input or output

        Args:
            :var_name: Variable name as used in the module code
            :default_value: default_value
            :unit: Unit of the required value, e.g. '[m/s]'
            :descr: Description of the input or output data
            :cpacs_path: CPACS node path
        """

        self.var_name = var_name
        self.default_value = default_value
        self.unit = unit
        self.descr = descr
        self.cpacs_path = cpacs_path


class CPACSInOut:

    def __init__(self):
        """
        Class summarising the input and output data
        """

        self.inputs = []
        self.outputs = []

    def add_input(self, **kwargs):
        entry = _Entry(**kwargs)
        self.inputs.append(entry)

    def add_output(self, **kwargs):
        if kwargs['default_value'] is not None:
            raise ValueError("Output 'default_value' must be None")

        entry = _Entry(**kwargs)
        self.outputs.append(entry)


#==============================================================================
#   FUNCTIONS
#==============================================================================

def check_cpacs_input_requirements(cpacs_file, cpacs_inout, module_file_name):
    """
    Check if the input CPACS file contains the required nodes
    """

    # log = get_logger(module_file_name.split('.')[0])

    required_inputs = cpacs_inout.inputs
    tixi = open_tixi(cpacs_file)

    missing_nodes = []
    for entry in required_inputs:
        if entry.default_value is not None:
            continue
        if tixi.checkElement(entry.cpacs_path) is False:
            missing_nodes.append(entry.cpacs_path)

    if missing_nodes:
        missing_str = ''
        for missing in missing_nodes:
            missing_str += '==> ' + missing + '\n'

        msg = f"CPACS path required but does not exist\n{missing_str}"
        # log.error(msg)
        raise CPACSRequirementError(msg)

    # TODO: close tixi handle?


#==============================================================================
#    MAIN
#==============================================================================

if __name__ == '__main__':

    log.info('Nothing to execute')

    # TODO: maybe add function to mange input/ouput, check double, write default /toolspecific ...