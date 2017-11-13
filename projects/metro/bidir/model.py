########
#IMPORTS
########

import sys
sys.path.insert(0, "./")

import random
import numpy

from mesa       import Agent, Model
from mesa.time  import RandomActivation
from mesa.space import MultiGrid

#############################
#FUNCTION: Chebyshev Distance
#############################

def chebyshev_dist(pos_a, pos_b):
    """
    Compute Chebyshev Distance in a grid enviroment.
    """
    return(max([abs(pos_a[0] - pos_b[0]), abs(pos_a[1] - pos_b[1])]))
    
#############################
#FUNCTION: Manhattan Distance
#############################  
    
def manhattan_dist(pos_a, pos_b):
    """
    Compute Manhattan Distance in a grid enviroment.
    """
    return(abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1]))

####################################
#FUNCTIONS: Ahead and Back Neigbhors
####################################
    
neighbors = numpy.array([(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)])

def ahead_neighbors(pos, orientation):
    """
    Return neighbor cells which are in front of an agent
    """
    return numpy.add(pos, neighbors[numpy.inner(orientation, neighbors) > 0])


def back_neighbors(pos, orientation):
    """
    Return neighbor cells which are in front of an agent
    """
    return numpy.add(pos, neighbors[numpy.inner(orientation, neighbors) > 0])

########################
#FUNCTION: Possibe moves
########################
    
def possible_moves(location, model):
    """
    Return all possible moves for a walker in a given location
    """
    neighbor_cells = model.grid.get_neighborhood(
        location,
        include_center = True,
        moore=model.moore_neighborhood)

    for neighbor in model.grid.neighbor_iter(location, moore = model.moore_neighborhood):
        if isinstance(neighbor, Walker) or isinstance(neighbor, Wall) and (neighbor.pos in neighbor_cells):
            neighbor_cells.remove(neighbor.pos)
    
    return neighbor_cells

####################
#CLASS: Walker Agent
####################

#Possible speeds for an agent
speeds = numpy.arange(0.40, 0.95, 0.05)
empathies = numpy.arange(0.40, 0.95, 0.05)
opposite_source = {"left": "right", "right": "left"}

class Walker(Agent):
    """
    An agent that moves toward the opposite gate
    """
    def __init__(self, unique_id, model, source, orientation):
        super().__init__(unique_id, model)
        self.speed = random.choice(speeds)
        self.empathy = random.choice(empathies)
        self.source = source
        self.orientation = orientation
        self.cant_move = 0
        
    def move_on(self):
        
        pm = possible_moves(self.pos, self.model)
        random.shuffle(pm)
        
        if pm:

            distances = numpy.zeros(len(pm))
            for index, move in enumerate(pm):
                #distances[index] = numpy.linalg.norm(numpy.subtract(self.model.gates_pos[opposite_source[self.source]], move)).min()
                distances[index] = 2*numpy.array([manhattan_dist(g.pos, move) for g in self.model.gates[opposite_source[self.source]]]).min()
                print(numpy.linalg.norm(numpy.subtract(move, self.pos)))
                distances[index] += numpy.linalg.norm(numpy.subtract(move, self.pos))
                if move == self.pos:
                    distances[index] += 1
    
            next_move = pm[distances.argmin()]
            if next_move != self.pos:
                self.orientation = (next_move[0]-self.pos[0], next_move[1]-self.pos[1])
                self.cant_move = 0
            else:
                self.cant_move += 1

            self.model.grid.move_agent(self, next_move)
        
    def step(self):       
        if random.random() < self.speed:
            if self.unique_id not in self.model.removals:
                self.move_on()
                
##################
#CLASS: Gate Agent
##################

walker_init_orient = {"left": (1, 0), "right": (-1, 0)}

class Gate(Agent):
    """
    An agent that creates and removes Walkers
    """
    def __init__(self, unique_id, model, gate_type):
        super().__init__(unique_id, model)
        self.gate_type = gate_type
        self.bidir = True
    
    def step(self):
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        foreign = [obj for obj in this_cell if (isinstance(obj, Walker) and obj.source != self.gate_type)]
        natives = [obj for obj in this_cell if (isinstance(obj, Walker) and obj.source == self.gate_type)]
        
        #Remove foreign walkers
        for f in foreign:
            self.model.grid._remove_agent(self.pos, f)
            self.model.schedule.remove(f)
            self.model.removals.append(f.unique_id)
        
        #Create native walkers
        if not natives:
            if (random.random() < self.model.gates_rates[self.gate_type]):
                p = Walker(self.model.agent_id, self.model, self.gate_type, walker_init_orient[self.gate_type])
                self.model.schedule.add(p)
                self.model.grid.place_agent(p, self.pos)
                self.model.agent_id += 1

##################
#CLASS: Wall Agent
##################

class Wall(Agent):
    """An agent that restrict Walker movements"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def step(self):
        pass
    
###################
#CLASS: Metro Model
###################

class MetroModel(Model):
    """
    Metro Station Model:
    There are two gates in opposite sides.
    Each gate has 
    """
    def __init__(self, width, height, leftRateSlider, rightRateSlider):
        #Model variables
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.removals = []
        self.leftRateSlider = leftRateSlider
        self.rightRateSlider = rightRateSlider
        self.agent_id = 0
        self.moore_neighborhood = True
        
        #Gates settings
        self.gates_rates = {"left":  self.leftRateSlider.value,
                            "right": self.rightRateSlider.value}
        
        self.gates = {"left": [], "right": []}
        gates_x = {"left": 0, "right": width-1}
        gates_y = {"left":  [21, 22, 23, 24, 25, 26],
                   "right": [ 3,  4,  5,  6,  7,  8]}
        
        #Create Gates
        for side in gates_y.keys():
            for l in gates_y[side]:
                g = Gate(self.agent_id, self, side)
                self.grid.place_agent(g, (gates_x[side], l))
                self.schedule.add(g)
                self.gates[side].append(g)
                self.agent_id += 1

        #Create Walls
        for i in (range(width)):
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, 0))
            self.agent_id += 1
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, height-1))
            self.agent_id += 1
        
        for side, x in gates_x.items():
            for i in (range(height)):
                if i not in gates_y[side]:
                    w = Wall(self.agent_id, self)
                    self.grid.place_agent(w, (x, i))
                    self.agent_id += 1
                    
        self.gates_pos = {"left": numpy.array([g.pos for g in self.gates["left"]]),
                          "right": numpy.array([g.pos for g in self.gates["right"]])}

    def step(self):
        self.gates_rates["left"] = self.leftRateSlider.value
        self.gates_rates["right"] = self.rightRateSlider.value
        self.removals = []
        self.schedule.step()