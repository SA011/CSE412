from math import log
from queue import Queue
MODLUS = 2147483647
MULT1 = 24112
MULT2 = 26143
BUSY = 3
IDLE = 2
ARRIVAL = 0
DEPART = 1
INF = 1e30


class LCGRAND:
    def __init__(self, z = 1973272912):
        self.z = z

    def rand(self):
        zi = self.z
        lowprd = (zi & 65535) * MULT1
        hi31 = (zi >> 16) * MULT1 + (lowprd >> 16)
        zi = ((lowprd & 65535) - MODLUS) + ((hi31 & 32767) << 16) + (hi31 >> 15)
        if zi < 0 :
            zi += MODLUS
        lowprd = (zi & 65535) * MULT2
        hi31 = (zi >> 16) * MULT2 + (lowprd >> 16)
        zi = ((lowprd & 65535) - MODLUS) + ((hi31 & 32767) << 16) + (hi31 >> 15)
        if zi < 0:
             zi += MODLUS
        self.z = zi
        return (zi >> 7 | 1) / 16777216.0


class SSQS:
    def __init__(self, mean_arrival, mean_service, total_delay, type_of_events = 2):
        self.mean_arrival = mean_arrival
        self.mean_service = mean_service
        self.total_delay = total_delay
        self.type_of_events = type_of_events
        self.event_counter = 0

        self.event_file = open('event_orders.txt', 'w')
        self.result_file = open('results.txt', 'w')
        
        self.customer_delayed = 0
        self.current_time = 0.0
        self.total_time_delay = 0.0
        self.total_area = 0.0
        self.queue_last_time = 0.0
        self.server_busy_start = 0.0
        self.server_utilization = 0.0

        self.lcg = LCGRAND()

        self.server_status = IDLE
        self.qLen = 0
        self.q = Queue()



        self.next_event = [0] * type_of_events

        self.next_event[ARRIVAL] = self.expon(self.mean_arrival)
        self.next_event[DEPART] = INF

        self.result_file.write('----Single-Server Queueing System----\n\n')
        self.result_file.write(f'Mean inter-arrival time: {mean_arrival:.6f} minutes\n')
        self.result_file.write(f'Mean service time: {mean_service:6f} minutes\n')
        self.result_file.write(f'Number of customers: {total_delay}\n\n')
            

    def schedule(self):
        self.event_counter += 1
        event_type = ARRIVAL
        
        if self.next_event[ARRIVAL] > self.next_event[DEPART]:
            event_type = DEPART
        
        self.current_time = self.next_event[event_type]
        if event_type == ARRIVAL:
            self.arrive()
        else:
            self.depart()

    def arrive(self):
        self.event_file.write(f'{self.event_counter}. Next event: Customer {self.qLen + self.customer_delayed + 1} Arrival\n')
       
        self.next_event[ARRIVAL] = self.current_time + self.expon(self.mean_arrival)
        self.last_arrival_time = self.current_time

        if self.server_status == BUSY:
            self.total_area += self.qLen * (self.current_time - self.queue_last_time)
            self.queue_last_time = self.current_time
            self.qLen += 1
            self.q.put(self.current_time)
        else:
            self.server_status = BUSY
            self.server_busy_start = self.current_time
            self.customerDelayed()
    
    def depart(self):
        self.event_file.write(f'{self.event_counter}. Next event: Customer {self.customer_delayed} Departure\n')
        
        if self.qLen == 0:
            self.next_event[DEPART] = INF
            self.server_utilization += self.current_time - self.server_busy_start
            self.server_status = IDLE
        else:
            self.total_area += self.qLen * (self.current_time - self.queue_last_time)
            self.queue_last_time = self.current_time
            self.qLen -= 1
            self.total_time_delay += self.current_time - self.q.get()
            self.customerDelayed()

    def customerDelayed(self):
        self.customer_delayed += 1
        self.next_event[DEPART] = self.current_time + self.expon(self.mean_service)

        self.event_file.write(f'\n---------No. of customers delayed: {self.customer_delayed}--------\n')
        

        if self.customer_delayed == self.total_delay:
            self.server_utilization += self.current_time - self.server_busy_start
            self.result_file.write(f'Avg delay in queue: {self.total_time_delay / self.total_delay:.6f} minutes\n')
            self.result_file.write(f'Avg number in queue: {self.total_area / self.current_time:.6f}\n')
            self.result_file.write(f'Server utilization: {self.server_utilization/self.current_time:.6f}\n')
            self.result_file.write(f'Time simulation ended: {self.current_time:.6f} minutes')
            exit(0)

        self.event_file.write('\n')

    def expon(self, mean):
        return -mean * log(self.lcg.rand())


if __name__ == '__main__':
    with open('in.txt', 'r') as inp:
        inputs = inp.readline().split()
        
        q = SSQS(float(inputs[0]), float(inputs[1]), int(inputs[2]))
        while True:
            q.schedule()