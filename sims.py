import time


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
            if c.cell_error() == True:
                return True
        return False
    def missing_cell_data(self):
        if self.cells.length() != 4:
            return True
    
class Accumulator:
    def __init__(self, modules, overcurrent_protection):
        self.modules = modules #5 element list of modules
        self.overcurrent_protection = overcurrent_protection
        self.battery_connection = False
        self.highV = False
        self.lowV = False

    def go_into_error(self):
        for m in self.modules:
            if m.mod_error():
                return True
            
class BMS_StateMachine:
    def __init__(self, accumulator):
        self.accumulator = accumulator
        self.driving = False
        self.charging = False
        self.BMS_indicator = False
        self.tractive_indicator = False
        self.tractive_system_on = False
    def shutdown_circuit(self):
        self.BMS_indicator = True
        self.tractive_indicator = True
        time.sleep(3) #take 3 seconds hopefully to turn off high voltage if it is on if not nothing new
        self.accumulator.highV = False
        self.tractive_system_on = False

    def charging_shutdown(self):
        pass #fix
    def initialize(self):
        #starting the car
        self.accumulator.lowV = True
        return self.calibrate(self) #fix to make it call calibrate aka transitioning to calibrate
    def calibrate(self):
        if self.accumulator.go_into_error() or self.accumulator.modules.missing_cell_data():
            return self.shutdown_circuit(self)

    