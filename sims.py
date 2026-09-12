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
        if len(self.cells) != 4:
            return True
        return False
    
class Accumulator:
    def __init__(self, modules, overcurrent_protection):
        self.modules = modules #5 element list of modules
        self.overcurrent_protection = overcurrent_protection #if bad == "broke" if good == "good"
        self.battery_connection = False
        self.highV = False
        self.lowV = False
        self.on = False

    def missing_data_error(self):
        for m in self.modules:
            if m.missing_cell_data():
                return True
        return False
    def volt_or_temp_error(self):
        for m in self.modules:
            if m.mod_error():
                return True
        if self.overcurrent_protection == "broke":
            return True
        return False
            
class BMS_StateMachine:
    def __init__(self, accumulator, driving_time, off_time, error_off_time):
        self.accumulator = accumulator
        self.driving = False
        self.charging = False
        self.BMS_indicator = False
        self.tractive_indicator = False
        self.IR_charge = 0
        self.driving_time = driving_time #set it equal to 0 if charging
        self.off_time = off_time
        self.error_off_time = error_off_time #set equal to 0 if not an error
    def shutdown_circuit(self):
        print('shutdown circuit')
        self.BMS_indicator = True
        self.tractive_indicator = True
        time.sleep(3) #take 3 seconds hopefully to turn off high voltage if it is on if not nothing new
        self.accumulator.highV = False
        self.accumulator.on = False
        return self.shutdown(self.error_off_time)
    def error(self):
        if self.accumulator.missing_data_error() or self.accumulator.volt_or_temp_error():
            return True
        return False
    def drive_or_charge(self):
        d_or_c = input("enter C for charging and D for driving")
        return d_or_c
    def initialize(self):
        #starting the car
        print('initialization')
        self.accumulator.lowV = True
        time.sleep(1)
        print('transition to calibrate')
        return self.calibrate()
    def calibrate(self):
        print('calibrate')
        if self.error():
            time.sleep(1)
            print('transition to shutdown circuit')
            return self.shutdown_circuit()
        time.sleep(1)
        print('transition to idle')
        return self.idle()  
    def idle(self):
        print("idle")
        self.accumulator.battery_connection = False
        #constantly checking requirements to see if it needs to open shutdown circuit
        #scaled down so only checking in once but in real car would have while in idle checking requirements constantly
        if self.error():
            time.sleep(1)
            print('transition to shutdown')
            return self.shutdown_circuit()
        which = self.drive_or_charge()
        #checking which state to go into based on if the battery is charging or not
        if which == "C":
            self.charging = True
            time.sleep(1)
            print('transition to charging')
            return self.charging_state()
        if which == "D":
            self.driving = True
            time.sleep(1)
            print('transition to precharge')
            return self.precharge()
    def precharge(self):
        print("precharge")
        self.IR_charge = 90 #intermediate relay required to reach 90%
        self.accumulator.highV = True #high voltage turned on now
        self.accumulator.battery_connection = True
        time.sleep(1)
        print('transition to ready to drive')
        return self.ready_to_drive(self.driving_time)
    def ready_to_drive(self, drive_time):
        #still constantly checking the battery but since scaled down will only check the conditions once
        """not safe to have car driving and randomly shut off so if time change it so sets a warning for driver
        to stop car and then open shutdown circuit to cool down battery"""
        if self.error():
            time.sleep(1)
            print('transition to shutdown')
            return self.shutdown_circuit()
        print("ready to drive!")
        time.sleep(1)
        return self.shutdown(drive_time)
    def shutdown(self, off_time):
        print("shutdown")
        self.BMS_indicator = False
        self.tractive_indicator = False
        self.IR_charge = 0
        self.driving = False
        time.sleep(off_time)
        print('car and bms is off')
        return "done" #in 
    def charging_shutdown(self):
        print("charging shutdown")
        time.sleep(3) #wait 3 secs to switch to low voltage only
        self.accumulator.highV = False
        self.charging = False #charging taken off until manually reset
        time.sleep(1)
        print('transition to idle')
        return self.idle()
    def charging_state(self):
        print("charging state")
        if self.error():
            time.sleep(1)
            print('transition to charging shutdown')
            return self.charging_shutdown()
        time.sleep(1)
        print('done charging. transitioning to shutoff')
        self.charging = False
        return self.shutdown(1)
#unit tests to simulate conditions !!!!!
class TestOne:
    #testing as if all conditions were met for driving/charging
    def __init__(self):
        self.cell_list = [Cell(3.0, 40), Cell(2.70, 45), Cell(3.50, 35), Cell(3.85, 53)]
        self.mod1 = Module("one", self.cell_list)
        self.mod2 = Module("two", self.cell_list)
        self.mod3 = Module("three", self.cell_list)
        self.mod4 = Module("four", self.cell_list)
        self.mod5 = Module("five", self.cell_list)
        self.mod_list = [self.mod1, self.mod2, self.mod3, self.mod4, self.mod5]
        self.accumulator = Accumulator(self.mod_list, "good")
        self.state_mach = BMS_StateMachine(self.accumulator, 3, 1, 0)
    def state_machine_sim(self):
        return self.state_mach.initialize()
if __name__ == "__main__":
    test = TestOne()
    test.state_machine_sim()
class TestTwo:
    #testing as if voltage condition not met
    def __init__(self):
        self.cell_list = [Cell(3.0, 40), Cell(2.70, 45), Cell(4.10, 35), Cell(3.85, 53)]
        self.mod1 = Module("one", self.cell_list)
        self.mod2 = Module("two", self.cell_list)
        self.mod3 = Module("three", self.cell_list)
        self.mod4 = Module("four", self.cell_list)
        self.mod5 = Module("five", self.cell_list)
        self.mod_list = [self.mod1, self.mod2, self.mod3, self.mod4, self.mod5]
        self.accumulator = Accumulator(self.mod_list, "good")
        self.state_mach = BMS_StateMachine(self.accumulator, 3, 1, 0)
    def state_machine_sim(self):
        return self.state_mach.initialize()
#if __name__ == "__main__":
    #test = TestTwo()
    #test.state_machine_sim()
class TestThree:
    #testing as if temp condition not met
    def __init__(self):
        self.cell_list = [Cell(3.0, 40), Cell(2.70, 45), Cell(3.55, 60), Cell(3.85, 53)]
        self.mod1 = Module("one", self.cell_list)
        self.mod2 = Module("two", self.cell_list)
        self.mod3 = Module("three", self.cell_list)
        self.mod4 = Module("four", self.cell_list)
        self.mod5 = Module("five", self.cell_list)
        self.mod_list = [self.mod1, self.mod2, self.mod3, self.mod4, self.mod5]
        self.accumulator = Accumulator(self.mod_list, "good")
        self.state_mach = BMS_StateMachine(self.accumulator, 3, 1, 0)
    def state_machine_sim(self):
        return self.state_mach.initialize()
#if __name__ == "__main__":
    #test = TestThree()
    #test.state_machine_sim()