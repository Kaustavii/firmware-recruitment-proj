max_cellV = 4.0
min_cellV = 2.5
min_cell_temp = 0
max_cell_temp = 55
class Cell:
    def __init__(self, voltage, temperature):
        self.voltage = voltage
        self.temperature = temperature
    def cell_error(self):
        if min_cellV <= self.voltage <= max_cellV and min_cell_temp <= self.temperature <= max_cell_temp:
            return False
        return True
class Module:
    def __init__(self, name, cells):
        self.name = name
        self.cells = cells
        #cells will be a 4 element list of cells
        #will scale the battery down to 5 modules instead of 10 to simplify simulation
    def mod_error(self):
        for c in self.cells:
            if c.will_error() == True:
                return True
        return False
class accumulator:
    def __init__(self):
        pass