class Inventory:
    def __init__(self, inital_level, K, i, h, p):
        self.level = inital_level
        self.holding_cost = 0
        self.shortage_cost = 0
        self.ordering_cost = 0
        self.K = K
        self.i = i
        self.h = h
        self.p = p
    
    def order(self, amount):
        self.level += amount
    
    def demand(self, amount):
        self.level -= amount

    def update_ordering_cost(self, amount):
        if amount > 0:
            self.ordering_cost += self.K + self.i * amount

    def update_holding_cost(self, interval):
        self.holding_cost += self.h * max(self.level, 0) * interval
    
    def update_shortage_cost(self, interval):
        self.shortage_cost += self.p * max(-self.level, 0) * interval

