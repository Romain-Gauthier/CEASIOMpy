"""
CEASIOMpy: Conceptual Aircraft Design Software

Developed by CFS ENGINEERING, 1015 Lausanne, Switzerland

Settings modifictions GUI for CEASIOMpy

Python version: >=3.7

| Author: Aidan Jungo
| Creation: 2019-09-05

TODO:

    * Add "mouse over" for description
    * messagebox and error detection could be improved
    * Add a function "modify name" for aeromap


"""

# =================================================================================================
#   IMPORTS
# =================================================================================================

import re
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ceasiompy.utils.ceasiomlogger import get_logger
from ceasiompy.utils.moduleinterfaces import (
    check_cpacs_input_requirements,
    get_specs_for_module,
    get_submodule_list,
    get_toolinput_file_path,
    get_tooloutput_file_path,
)
from cpacspy.cpacsfunctions import (
    create_branch,
    get_string_vector,
    get_value,
    get_value_or_default,
)
from cpacspy.cpacspy import CPACS

log = get_logger()

MODULE_DIR = Path(__file__).parent
MODULE_NAME = MODULE_DIR.name


# =================================================================================================
#   CLASSES
# =================================================================================================


class AeroMapTab:
    """Class to create the AeroMap tab from the infomation in cpacs file."""

    def __init__(self, tabs, cpacs, aeromap_uid_list):
        """AeroMapTab class

        Args:
            tabs (object): Tab object
            cpacs (object): CPACS object created by cpacspy
            aeromap_uid_list (list): List of aeromap uid

        """

        self.tabs = tabs
        self.cpacs = cpacs
        row_pos = 0

        self.aerotab = tk.Frame(self.tabs, borderwidth=1)
        tabs.add(self.aerotab, text="AeroMaps")

        self.selected_list = []
        self.list = aeromap_uid_list

        # tk.Label(self.aerotab, text='Existing AeroMaps').grid(column=0, row=row_pos)
        # row_pos += 1

        self.existframe = tk.LabelFrame(self.aerotab, text="Existing AeroMaps")
        self.existframe.grid(row=row_pos, column=0, padx=15, pady=15)

        self.listBox = tk.Listbox(self.existframe, width=25, selectmode=tk.SINGLE)
        item_count = len(self.list)
        self.listBox.grid(column=0, row=row_pos, rowspan=item_count, padx=5, pady=5)
        self.list.sort()
        for item in self.list:
            self.listBox.insert(tk.END, item)
        row_pos += item_count + 1

        importButton = tk.Button(
            self.existframe, text="Import from CSV", width=15, command=self._import_csv
        )
        importButton.grid(column=0, row=row_pos)
        row_pos += 1

        exportButton = tk.Button(
            self.existframe, text="Export to CSV", width=15, command=self._export_csv
        )
        exportButton.grid(column=0, row=row_pos)
        row_pos += 1

        checkButton = tk.Button(
            self.existframe, width=15, text="Check AeroMap", command=self._check_aeromap
        )
        checkButton.grid(column=0, row=row_pos)
        row_pos += 1

        deleteButton = tk.Button(self.existframe, text="Delete", width=15, command=self._delete)
        deleteButton.grid(column=0, row=row_pos)

        # To generate a new aeromap on the GUI
        row_pos = 0
        self.generateframe = tk.LabelFrame(self.aerotab, text="Generate an AeroMap")
        self.generateframe.grid(row=row_pos, column=1, padx=15, pady=15, sticky=tk.N)

        self.labelaeromap = tk.Label(self.generateframe, text="Name")
        self.labelaeromap.grid(row=row_pos, column=0, pady=3)
        self.aeromap_name = tk.StringVar()
        self.aeromap_name.set("MyNewAeroMap")
        self.name = tk.Entry(self.generateframe, width=17, textvariable=self.aeromap_name)
        self.name.grid(row=row_pos, column=1)
        row_pos += 1

        altlabel = tk.Label(self.generateframe, text="Altitude")
        altlabel.grid(row=row_pos, column=0, pady=3)
        self.alt = tk.StringVar()
        self.alt.set("0")
        altentry = tk.Entry(self.generateframe, textvariable=self.alt, width=17)
        altentry.grid(row=row_pos, column=1)
        altunitlabel = tk.Label(self.generateframe, text="[m]")
        altunitlabel.grid(column=2, row=row_pos)
        row_pos += 1

        machlabel = tk.Label(self.generateframe, text="Mach")
        machlabel.grid(row=row_pos, column=0, pady=3)
        self.mach = tk.StringVar()
        self.mach.set("0.3")
        machentry = tk.Entry(self.generateframe, textvariable=self.mach, width=17)
        machentry.grid(row=row_pos, column=1, pady=3)
        machunitlabel = tk.Label(self.generateframe, text="[-]")
        machunitlabel.grid(column=2, row=row_pos)
        row_pos += 1

        aoalabel = tk.Label(self.generateframe, text="AoA")
        aoalabel.grid(row=row_pos, column=0, pady=3)
        self.aoa = tk.StringVar()
        self.aoa.set("2")
        aoaentry = tk.Entry(self.generateframe, textvariable=self.aoa, width=17)
        aoaentry.grid(row=row_pos, column=1)
        aoaunitlabel = tk.Label(self.generateframe, text="[deg]")
        aoaunitlabel.grid(column=2, row=row_pos)
        row_pos += 1

        aoslabel = tk.Label(self.generateframe, text="AoS")
        aoslabel.grid(row=row_pos, column=0, pady=3)
        self.aos = tk.StringVar()
        self.aos.set("0")
        aosentry = tk.Entry(self.generateframe, textvariable=self.aos, width=17)
        aosentry.grid(row=row_pos, column=1)
        aosunitlabel = tk.Label(self.generateframe, text="[deg]")
        aosunitlabel.grid(column=2, row=row_pos)
        row_pos += 1

        self.genbutton = tk.Button(
            self.generateframe, text="Generate", command=self._generate_aeromap
        )
        self.genbutton.grid(row=row_pos, column=1, pady=3)
        row_pos += 1

    def _generate_aeromap(self, event=None):

        # Check if the name is already in the list
        if self.aeromap_name.get() in self.list:
            messagebox.showwarning("Warning", "AeroMap with this name already exists!")
            return

        # Transfrom entries in list
        alt_list = [float(alt) for alt in self.alt.get().split(";") if alt]
        mach_list = [float(mach) for mach in self.mach.get().split(";") if mach]
        aos_list = [float(aos) for aos in self.aos.get().split(";") if aos]
        aoa_list = [float(aoa) for aoa in self.aoa.get().split(";") if aoa]

        if len(alt_list) == len(mach_list) == len(aoa_list) == len(aos_list):
            aeromap = self.cpacs.create_aeromap(self.aeromap_name.get())
            aeromap.description = f"Created with CEASIOMpy SettingGui on {date_time_str()}"
            for alt, mach, aos, aoa in zip(alt_list, mach_list, aos_list, aoa_list):
                aeromap.add_row(alt=alt, mach=mach, aoa=aoa, aos=aos)
            aeromap.save()
        else:
            messagebox.showwarning("Warning", "Parameter lists must have the same lenght!")
            return

        self.listBox.selection_clear(0, tk.END)
        self._update()

    def _import_csv(self, event=None):
        template_csv_dir = Path(MODULE_DIR.parents[1], "test_files", "AeroMaps")
        csv_path = Path(
            filedialog.askopenfilename(initialdir=template_csv_dir, title="Select a CSV file")
        )

        aeromap_uid = csv_path.name

        if aeromap_uid in self.list:
            messagebox.showwarning("Warning", "AeroMap with this name already exists!")
            return

        aeromap = self.cpacs.create_aeromap_from_csv(csv_path, aeromap_uid)
        aeromap.description = (
            f"Created with CEASIOMpy SettingGui, "
            f"imported from '{csv_path}' on {date_time_str()}"
        )
        aeromap.save()

        self.listBox.selection_clear(0, tk.END)
        self._update()

    def _export_csv(self, event=None):

        aeromap_uid_list = [self.listBox.get(i) for i in self.listBox.curselection()]
        csv_path = filedialog.asksaveasfilename(
            initialdir=MODULE_DIR, title="Save CSV file", defaultextension=".csv"
        )

        aeromap = self.cpacs.get_aeromap_by_uid(aeromap_uid_list[0])
        aeromap.export_csv(csv_path)

        self.listBox.selection_clear(0, tk.END)

    def _update(self, event=None):

        self.list = self.cpacs.get_aeromap_uid_list()
        self.list.sort()
        self.listBox.delete(0, tk.END)
        for item in self.list:
            self.listBox.insert(tk.END, item)

    def _check_aeromap(self, event=None):
        self.selected_list = [self.listBox.get(i) for i in self.listBox.curselection()]
        aeromap_uid = self.selected_list[0]
        aeromap = self.cpacs.get_aeromap_by_uid(aeromap_uid)
        print(aeromap)

    def _delete(self, event=None):
        self.selected_list = [self.listBox.get(i) for i in self.listBox.curselection()]
        aeromap_uid = self.selected_list[0]
        self.cpacs.delete_aeromap(aeromap_uid)
        self._update()

    # def _modify_name(self, event = None):
    # TODO

    def returnValue(self):
        self.master.wait_window()
        return self.selected_list


class AutoTab:
    """Class to create automatically tabs from the infomation in the __specs__
    file of each module."""

    def __init__(self, tabs, cpacs, module_name):
        """Tab class

        Note:
            A tab will only be created if the module actually has
            any settings which are to be shown

        Args:
            tabs (object): Tab object
            cpacs (object): CPACS object
            module_name (str): String of the module name for which a tab is to be created
        """

        self.var_dict = {}
        self.group_dict = {}

        self.module_name = module_name
        self.tabs = tabs
        self.cpacs = cpacs
        self.tab = tk.Frame(tabs, borderwidth=1)
        tabs.add(self.tab, text=module_name)

        # Get GUI dict from specs
        specs = get_specs_for_module(module_name)

        self.gui_dict = specs.cpacs_inout.get_gui_dict()

        # canvas has replaced self.tab in the following lines
        space_label = tk.Label(self.tab, text=" ")
        space_label.grid(column=0, row=0)

        row_pos = 1

        for (
            key,
            (name, def_value, dtype, unit, xpath, description, group),
        ) in self.gui_dict.items():
            # Create a LabelFrame for new groupe
            if group:
                if group not in self.group_dict:
                    self.labelframe = tk.LabelFrame(self.tab, text=group)
                    self.labelframe.grid(
                        column=0, row=row_pos, columnspan=3, sticky=tk.W, padx=15, pady=5
                    )
                    self.group_dict[group] = self.labelframe
                parent = self.group_dict[group]
            else:  # if not a group, use tab as parent
                parent = self.tab

            # Name label for variable
            if name not in ["__AEROMAP_SELECTION", "__AEROMAP_CHECHBOX"]:
                self.name_label = tk.Label(parent, text=name)
                self.name_label.grid(column=0, row=row_pos, sticky=tk.W, padx=5, pady=5)

            # Type and Value
            if dtype is bool:
                self.var_dict[key] = tk.BooleanVar()
                value = get_value_or_default(self.cpacs.tixi, xpath, def_value)
                self.var_dict[key].set(value)
                bool_entry = tk.Checkbutton(parent, text="", variable=self.var_dict[key])
                bool_entry.grid(column=1, row=row_pos, padx=5, pady=5)

            elif dtype is int:
                value = get_value_or_default(self.cpacs.tixi, xpath, def_value)
                self.var_dict[key] = tk.IntVar()
                self.var_dict[key].set(int(value))
                value_entry = tk.Entry(parent, bd=2, width=8, textvariable=self.var_dict[key])
                value_entry.grid(column=1, row=row_pos, padx=5, pady=5)

            elif dtype is float:
                value = get_value_or_default(self.cpacs.tixi, xpath, def_value)
                self.var_dict[key] = tk.DoubleVar()
                self.var_dict[key].set(value)
                value_entry = tk.Entry(parent, bd=2, width=8, textvariable=self.var_dict[key])
                value_entry.grid(column=1, row=row_pos, padx=5, pady=5)

            elif dtype == "pathtype":

                value = get_value_or_default(self.cpacs.tixi, xpath, def_value)
                self.var_dict[key] = tk.StringVar()
                self.var_dict[key].set(value)
                value_entry = tk.Entry(parent, textvariable=self.var_dict[key])
                value_entry.grid(column=1, row=row_pos, padx=5, pady=5)

                self.key = key
                self.browse_button = tk.Button(parent, text="Browse", command=self._browse_file)
                self.browse_button.grid(column=2, row=row_pos, padx=5, pady=5)

            elif dtype is list:
                if name == "__AEROMAP_SELECTION":

                    # Get the list of all AeroMaps
                    self.aeromap_uid_list = self.cpacs.get_aeromap_uid_list()

                    # Try to get the pre-selected AeroMap from the xpath
                    try:
                        selected_aeromap = get_value(self.cpacs.tixi, xpath)
                        selected_aeromap_index = self.aeromap_uid_list.index(selected_aeromap)
                    except ValueError:
                        selected_aeromap = ""
                        selected_aeromap_index = 0

                    self.labelframe = tk.LabelFrame(parent, text="Choose an AeroMap")
                    self.labelframe.grid(
                        column=0, row=row_pos, columnspan=3, sticky=tk.W, padx=15, pady=5
                    )

                    # The Combobox is directly use as the variable
                    self.var_dict[key] = ttk.Combobox(
                        self.labelframe, values=self.aeromap_uid_list
                    )
                    self.var_dict[key].current(selected_aeromap_index)
                    self.var_dict[key].grid(column=1, row=row_pos, padx=15, pady=5)

                elif name == "__AEROMAP_CHECHBOX":

                    # Just to find back the name when data are saved
                    self.var_dict[key] = None
                    # __AEROMAP_CHECHBOX is a bit different, data are saved in their own dictionary
                    self.aeromap_var_dict = {}

                    # Get the list of all AeroMaps
                    self.aeromap_uid_list = self.cpacs.get_aeromap_uid_list()
                    self.labelframe = tk.LabelFrame(parent, text="Selecte AeroMap(s)")
                    self.labelframe.grid(
                        column=0, row=row_pos, columnspan=3, sticky=tk.W, padx=15, pady=5
                    )

                    # Try to get pre-selected AeroMaps from the xpath
                    try:
                        selected_aeromap = get_string_vector(self.cpacs.tixi, xpath)
                    except ValueError:
                        selected_aeromap = ""

                    # Create one checkbox for each AeroMap
                    for aeromap in self.aeromap_uid_list:
                        self.aeromap_var_dict[aeromap] = tk.BooleanVar()

                        # if aeromap in selected_aeromap:
                        # For now, set all to True
                        self.aeromap_var_dict[aeromap].set(True)

                        aeromap_entry = tk.Checkbutton(
                            self.labelframe, text=aeromap, variable=self.aeromap_var_dict[aeromap]
                        )
                        aeromap_entry.pack(padx=5, pady=3, anchor=tk.W)  # side=tk.TOP)

                else:  # Other kind of list (not aeroMap)

                    # 'def_value' will be the list of possibilities in this case

                    # Try to get the pre-selected AeroMap from the xpath
                    try:  # TODO Should be retested...
                        selected_value = get_value(self.cpacs.tixi, xpath)
                        selected_value_index = def_value.index(selected_value)
                    except:
                        selected_value = ""
                        selected_value_index = 0

                    # The Combobox is directly use as the variable
                    self.var_dict[key] = ttk.Combobox(parent, width=12, values=def_value)
                    self.var_dict[key].current(selected_value_index)
                    self.var_dict[key].grid(column=1, row=row_pos, padx=5, pady=5)

            else:
                value = get_value_or_default(self.cpacs.tixi, xpath, def_value)
                self.var_dict[key] = tk.StringVar()
                self.var_dict[key].set(value)
                value_entry = tk.Entry(parent, textvariable=self.var_dict[key])
                value_entry.grid(column=1, row=row_pos, padx=5, pady=5)

            # Units
            if unit and unit != "1":
                unit_label = tk.Label(parent, text=pretty_unit(unit))
                unit_label.grid(column=2, row=row_pos)

            row_pos += 1

    def _browse_file(self):

        self.filename = filedialog.askopenfilename(initialdir=MODULE_DIR, title="Select A File")
        self.var_dict[self.key].set(self.filename)


class SettingGUI(tk.Frame):
    """Main window. All the other widgets are stored in this window."""

    def __init__(self, master, cpacs_path, cpacs_out_path, submodule_list, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.pack(fill=tk.BOTH)

        self.submodule_list = submodule_list
        self.cpacs_out_path = cpacs_out_path

        # Notebook for tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=0, column=0, columnspan=3)  # pack()#expand=1, side=tk.LEFT)

        # Open the cpacs file
        self.cpacs = CPACS(cpacs_path)

        aeromap_uid_list = self.cpacs.get_aeromap_uid_list()
        if not aeromap_uid_list:
            csv_path = Path(MODULE_DIR.parents[1], "test_files", "AeroMaps", "Aeromap_1point.csv")
            new_aeromap = self.cpacs.create_aeromap_from_csv(csv_path, "AeroMap_1point")
            new_aeromap.save()
            aeromap_uid_list = self.cpacs.get_aeromap_uid_list()

        # Generate AeroMaps Edition tab
        AeroMapTab(self.tabs, self.cpacs, aeromap_uid_list)

        # Generate Auto Tab =============
        self.tab_list = []
        self._update_all()

        # Check windows size to change position of button if too small
        row = 1
        col = 1
        if self.winfo_screenheight() < 1000:
            row = 0
            col = 3

        # General button
        self.update_button = tk.Button(self, text="Update", command=self._update_all)
        self.update_button.grid(row=row, column=col, sticky="E")
        self.close_button = tk.Button(self, text="Save & Quit", command=self._save_quit)
        self.close_button.grid(row=row, column=col + 1, sticky="W")

    def _update_all(self):

        # Remove existing AutoTab
        if len(self.tab_list) > 0:
            for i in range(len(self.tab_list)):
                self.tabs.forget(1)
            self.tab_list = []

        # Generate new Auto Tab
        for module_name in self.submodule_list:

            specs = get_specs_for_module(module_name)
            if specs is None:  # Specs does not exist
                continue
            self.gui_dict = specs.cpacs_inout.get_gui_dict()
            if not self.gui_dict:  # Empty dict --> nothing to do
                continue

            tab = AutoTab(self.tabs, self.cpacs, module_name)
            self.tab_list.append(tab)

    def _save_quit(self):

        # Iterate over all existing tabs
        for tab in self.tab_list:
            # Iterate in Variable dictionary of each tab
            for key, var in tab.var_dict.items():
                # Get the XPath from the GUI setting dictionary and crate a branch
                name = tab.gui_dict[key][0]
                xpath = tab.gui_dict[key][4]
                create_branch(self.cpacs.tixi, xpath)
                if name == "__AEROMAP_CHECHBOX":
                    aeromap_uid_list_str = ""
                    for aeromap_uid, aeromap_bool in tab.aeromap_var_dict.items():
                        if aeromap_bool.get():
                            aeromap_uid_list_str += aeromap_uid + ";"
                    if aeromap_uid_list_str == "":
                        messagebox.showerror(
                            "ValueError",
                            'In the Tab "'
                            + tab.module_name
                            + '", no value has been selected for "'
                            + name
                            + '" ',
                        )
                        raise TypeError("No value has been selected for " + name + " !")
                    self.cpacs.tixi.updateTextElement(xpath, aeromap_uid_list_str)

                # '__AEROMAP_SELECTION' and list Type value will be saved as any other variable
                else:
                    if str(var.get()) == "":
                        # Not working when it expect an 'int' or a 'float'
                        messagebox.showerror(
                            "ValueError",
                            'In the Tab "'
                            + tab.module_name
                            + '", no value has been entered for "'
                            + name
                            + '" ',
                        )
                        raise TypeError("No value has been entered for " + name + " !")

                    try:
                        self.cpacs.tixi.updateTextElement(xpath, str(var.get()))
                    except:

                        messagebox.showerror(
                            "TypeError",
                            'In the Tab "'
                            + tab.module_name
                            + '", the value "'
                            + name
                            + '" has not the correct type!',
                        )
                        raise TypeError(name + " has not the correct type!")

        self.cpacs.save_cpacs(self.cpacs_out_path, overwrite=True)

        self.quit()


# =================================================================================================
#   FUNCTIONS
# =================================================================================================


def date_time_str():
    """Return the current date and time as a string."""

    return datetime.now().strftime("%Y-%m-%d at %H:%M:%S")


def pretty_unit(unit_string):
    """Prettify a unit string

    Args:
        unit_string (str): Unit string

    Returns:
        pretty_unit (str): Prettified unit string
    """

    unit_string = pretty_exponent(unit_string)
    unit_string = wrap_in_brackets(unit_string, space=1)
    return unit_string


def pretty_exponent(string):
    """Prettify a numeric exponent in a string

    Args:
        string (str): String to prettify

    returns:
        pretty_string (str): Prettified string
    """

    def make_exp(string):
        # There must be a better way...
        replace_table = ("0⁰", "1¹", "2²", "3³", "4⁴", "5⁵", "6⁶", "7⁷", "8⁸", "9⁹")
        for sub in replace_table:
            string = string.replace(sub[0], sub[1])
        return string

    number_exp = re.compile(r"\^[0-9]*")
    matches = number_exp.findall(string)

    for match in matches:
        string = string.replace(match, make_exp(match[1:]))

    return string


def wrap_in_brackets(string, brackets="[]", space=0):
    """Add enclosing square brackets to a string if not yet existing

    Examples:

    >>> wrap_in_brackets("test")
    '[test]'
    >>> wrap_in_brackets("[m/s]")
    '[m/s]'
    >>> wrap_in_brackets("[m/s")
    '[m/s]'
    >>> wrap_in_brackets("m/s")
    '[m/s]'

    Args:
        string (str): String to wrap
        brackets (str): String of length 2 with opening/closing bracket
        space (int): Number of spaces between bracket and string
    """

    # Cut leading/trailing brackets
    while string.startswith(brackets[0]):
        string = string[1:]
    while string.endswith(brackets[1]):
        string = string[:-1]

    return f"[{' '*space}{string}{' '*space}]"


def create_settings_gui(cpacs_path, cpacs_out_path, submodule_list):
    """Create a GUI with Tkinter to fill CEASIOMpy settings

    Args:
        cpacs_path (str): Path to the CPACS file
        cpacs_out_path (str): Path to the output CPACS file
        submodule_list (list): List of module to include in the GUI

    """

    root = tk.Tk()
    root.title("CEASIOMpy Settings GUI")

    # Automatically set the size of the windows
    gui_modules = 1
    max_inputs = 0
    for module_name in submodule_list:
        specs = get_specs_for_module(module_name)
        if specs:
            inputs = specs.cpacs_inout.get_gui_dict()
            if inputs:
                gui_modules += 1
                max_inputs = max(max_inputs, len(inputs))

    tot_width = max(415, gui_modules * 82)
    tot_height = max(350, max_inputs * 50)
    root.geometry(f"{tot_width}x{tot_height}+400+150")

    my_setting_gui = SettingGUI(root, cpacs_path, cpacs_out_path, submodule_list)
    my_setting_gui.mainloop()
    root.iconify()
    root.destroy()


# =================================================================================================
#    MAIN
# =================================================================================================

if __name__ == "__main__":

    log.info("----- Start of " + MODULE_NAME + " -----")

    cpacs_path = get_toolinput_file_path(MODULE_NAME)
    cpacs_out_path = get_tooloutput_file_path(MODULE_NAME)

    check_cpacs_input_requirements(cpacs_path)
    create_settings_gui(cpacs_path, cpacs_out_path, get_submodule_list())

    log.info("----- End of " + MODULE_NAME + " -----")
