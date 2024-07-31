from Inventory import Inventory
from LCGRAND import *
import argparse
lcg = LCGRAND()

class Order_arrival:
    def __init__(self, inventory, minlag, maxlag):
        self.inventory = inventory
        self.order = 0
        self.time = inf
        self.minlag = minlag
        self.maxlag = maxlag

    def process(self):
        self.inventory.order(self.order)
        self.time = inf
    
    def schedule(self, time, order):
        self.time = time + lcg.uniform(self.minlag, self.maxlag)
        self.order = order
        self.inventory.update_ordering_cost(order)

class Demand_arrival:
    def __init__(self, inventory, mean_interdemand, demand_distribution):
        self.inventory = inventory
        self.demand = 0
        self.mean_interdemand = mean_interdemand
        self.time = lcg.expon(self.mean_interdemand)
        self.demand_distribution = demand_distribution

    def process(self):
        self.schedule()
        self.inventory.demand(self.demand)
    
    def schedule(self):
        rand = lcg.rand()
        self.demand = 0
        while rand >= self.demand_distribution[self.demand]:
            self.demand += 1
        self.demand += 1
        self.time = self.time + lcg.expon(self.mean_interdemand)


    
class End_simulation:
    def __init__(self, time):
        self.time = time
    
    def process(self):
        pass

    def schedule(self, time):
        pass

class Evaluate:
    def __init__(self, inventory, order_event, s, S):
        self.inventory = inventory
        self.time = 0
        self.order_event = order_event
        self.s = s
        self.S = S

    def process(self):
        if self.inventory.level < self.s:
            self.order_event.schedule(self.time, self.S - self.inventory.level)
        
        self.schedule()
    
    def schedule(self):
        self.time += 1

class Inventory_simulator:
    def __init__(self, input_file, output_file):
        self.inp = open(input_file, 'r')
        self.out = open(output_file, 'w')

        self.I, self.N, self.P = list(map(int, self.inp.readline().split()))
        self.D, self.beta_D = list(map(float, self.inp.readline().split()))
        self.K, self.i, self.h, self.pi = list(map(float, self.inp.readline().split()))
        self.m, self.M = list(map(float, self.inp.readline().split()))
        self.demand_probablity = list(map(float, self.inp.readline().split()))
        self.s, self.S = 0, 0
        self.inventory = None
        self.time = 0.0
        self.events = []
        self.D = int(self.D)

        ##########Print Initial Values##########
        self.out.write("------Single-Product Inventory System------\n\n")
        self.out.write(f"Initial inventory level: {self.I} items\n\n")
        self.out.write(f"Number of demand sizes: {self.D}\n\n")
        self.out.write(f"Distribution function of demand sizes:")
        for i in range(self.D):
            self.out.write(f" {self.demand_probablity[i]:.2f}")
        self.out.write("\n\n")
        self.out.write(f"Mean inter-demand time: {self.beta_D:.2f} months\n\n")
        self.out.write(f"Delivery lag range: {self.m:.2f} to {self.M:.2f} months\n\n")
        self.out.write(f"Length of simulation: {self.N} months\n\n")
        self.out.write("Costs:\n")
        self.out.write(f"K = {self.K:.2f}\n")
        self.out.write(f"i = {self.i:.2f}\n")
        self.out.write(f"h = {self.h:.2f}\n")
        self.out.write(f"pi = {self.pi:.2f}\n\n")
        self.out.write(f"Number of policies: {self.P}\n\n")
        self.out.write("Policies:\n")
        self.out.write("--------------------------------------------------------------------------------------------------\n")
        self.out.write(" Policy        Avg_total_cost     Avg_ordering_cost      Avg_holding_cost     Avg_shortage_cost\n")
        self.out.write("--------------------------------------------------------------------------------------------------\n")
    
    def setupPolicy(self):
        if self.P == 0:
            return False
        self.s, self.S = list(map(int, self.inp.readline().split()))
        self.inventory = Inventory(self.I, self.K, self.i, self.h, self.pi)
        self.time = 0.0
        self.events = []
        self.events.append(Order_arrival(self.inventory, self.m, self.M))
        self.events.append(Demand_arrival(self.inventory, self.beta_D, self.demand_probablity))
        self.events.append(End_simulation(self.N))
        self.events.append(Evaluate(self.inventory, self.events[0], self.s, self.S))
        self.P -= 1
        return True
    
    def run(self):
        while True:
            next_event = self.events[0]
            for event in self.events:
                if event.time < next_event.time:
                    next_event = event
                
            # for event in self.events:
            #     print(f"{event.time:.2f}", end = " ")
            # print()
            self.inventory.update_holding_cost(next_event.time - self.time)
            self.inventory.update_shortage_cost(next_event.time - self.time)
            self.time = next_event.time
            next_event.process()
            if isinstance(next_event, End_simulation):
                avg_total_cost = (self.inventory.holding_cost + self.inventory.shortage_cost + self.inventory.ordering_cost) / self.N
                avg_ordering_cost = self.inventory.ordering_cost / self.N
                avg_holding_cost = self.inventory.holding_cost / self.N
                avg_shortage_cost = self.inventory.shortage_cost / self.N
                
                self.out.write("\n")
                self.out.write(f"({self.s},{self.S:3d})")
                self.out.write(f"{avg_total_cost:20.2f}")
                self.out.write(f"{avg_ordering_cost:20.2f}")
                self.out.write(f"{avg_holding_cost:20.2f}")
                self.out.write(f"{avg_shortage_cost:20.2f}\n")
                break
    def end(self):
        self.out.write("\n--------------------------------------------------------------------------------------------------")
        self.out.close()
        self.inp.close()

argparser = argparse.ArgumentParser()
argparser.add_argument("--path", help = "path to i/o folder", default = "io1")
args = argparser.parse_args()


dir = args.path        

input_file = dir + "/in.txt"
output_file = dir + "/output.txt"
simulator = Inventory_simulator(input_file, output_file)

while simulator.setupPolicy():
    simulator.run()
            
simulator.end()