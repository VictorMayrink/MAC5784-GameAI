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

############################
#FUNCTION: Diagonal distance
############################

def diagonal_dist(pos, goal, D1=1, D2= 1.4142135623730951):
    dx = abs(pos[0] - goal[0])
    dy = abs(pos[1] - goal[1])
    return(D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy))

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
    
def possible_moves(walker, model):
    """
    Return all possible moves for a walker in a given location
    """
    neighbor_cells = model.grid.get_neighborhood(
        walker.pos,
        include_center = True,
        moore=model.moore_neighborhood)

    for neighbor in model.grid.neighbor_iter(walker.pos, moore = model.moore_neighborhood):
        if ((isinstance(neighbor, Walker) or 
            isinstance(neighbor, Wall) or 
            isinstance(neighbor, Entry)) and
            (neighbor.pos in neighbor_cells)):
                neighbor_cells.remove(neighbor.pos)
    
    return neighbor_cells

####################
#CLASS: Walker Agent
####################

#Possible speeds for an agent
speeds = numpy.arange(0.40, 0.95, 0.05)
opposite_source = {"left": "right", "right": "left"}

class Walker(Agent):
    """
    An agent that moves toward the opposite gate
    """
    def __init__(self, unique_id, model, source, orientation):
        super().__init__(unique_id, model)
        self.speed = random.choice(speeds)
        self.impatience = 1
        self.source = source
        self.orientation = orientation
        self.cant_move = 0
        
        
    def move_on(self):
        
        pm = possible_moves(self, self.model)
        random.shuffle(pm)
        
        if pm:
            distances = numpy.zeros(len(pm))
            cost = numpy.zeros(len(pm))
            for index, move in enumerate(pm):
                distances[index] = numpy.array([diagonal_dist(g.pos, move) + numpy.linalg.norm(numpy.subtract(move, self.pos)) for g in self.model.exits[opposite_source[self.source]]]).min()
                distances[index] += random.random()/10000
                cost[index] = distances[index]# + 0*self.model.influence_map[tuple(numpy.add(move, self.model.padding))]
                if move == self.pos:
                    cost[index] += self.impatience

            next_move = pm[cost.argmin()]
            if next_move != self.pos:
                self.orientation = (next_move[0]-self.pos[0], next_move[1]-self.pos[1])
                self.cant_move = 0
            else:
                self.cant_move += 1

            self.model.influence_map[
                self.pos[0]:(self.pos[0]+len(self.model.influence_mask)),
                self.pos[1]:(self.pos[1]+len(self.model.influence_mask))] -= self.model.influence_mask
            self.model.grid.move_agent(self, next_move)
            self.model.influence_map[
                self.pos[0]:(self.pos[0]+len(self.model.influence_mask)),
                self.pos[1]:(self.pos[1]+len(self.model.influence_mask))] += self.model.influence_mask
        
    def step(self):       
        if random.random() < self.speed:
            if self.unique_id not in self.model.removals:
                self.move_on()
                
######################
#CLASS: Entrance Agent
######################

walker_init_orient = {"left": (1, 0), "right": (-1, 0)}

class Entry(Agent):
    """
    An agent that creates Walkers
    """
    def __init__(self, unique_id, model, entry_type):
        super().__init__(unique_id, model)
        self.entry_type = entry_type
    
    def step(self):
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        contents = [obj for obj in this_cell if isinstance(obj, Walker)]
        #Create native walkers
        if not contents:
            if (random.random() < self.model.entry_rates[self.entry_type]):
                p = Walker(self.model.agent_id, self.model, self.entry_type, walker_init_orient[self.entry_type])
                self.model.schedule.add(p)
                self.model.grid.place_agent(p, self.pos)
                self.model.agent_id += 1
                self.model.influence_map[
                        self.pos[0]:(self.pos[0]+len(self.model.influence_mask)),
                        self.pos[1]:(self.pos[1]+len(self.model.influence_mask))] += self.model.influence_mask

##################
#CLASS: Exit Agent
##################
        
class Exit(Agent):
    """
    An agent that creates Walkers
    """
    def __init__(self, unique_id, model, exit_type):
        super().__init__(unique_id, model)
        self.exit_type = exit_type
    
    def step(self):
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        foreign = [obj for obj in this_cell if (isinstance(obj, Walker) and obj.source != self.exit_type)]
        
        #Remove foreign walkers
        for f in foreign:
            self.model.grid._remove_agent(self.pos, f)
            self.model.schedule.remove(f)
            self.model.removals.append(f.unique_id)

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
        self.padding=2
        self.influence_mask = numpy.array(
            [[0, 1, 1, 1, 0],
             [1, 2, 3, 2, 1],
             [1, 3, 4, 3, 1],
             [1, 2, 3, 2, 1],
             [0, 1, 1, 1, 0]])
        self.influence_map = numpy.zeros((width+2*self.padding, height+2*self.padding))
        
        #Gates settings
        self.entry_rates = {"left":  self.leftRateSlider.value,
                            "right": self.rightRateSlider.value}
        
        self.entries = {"left": [], "right": []}
        entries_x = {"left": 0, "right": width-1}
        entries_y = {"left":  [19, 20, 21, 22],
                     "right": [ 7,  8, 9, 10]}
        self.exits = {"left": [], "right": []}
        exits_x = {"left": 0, "right": width-1}
        exits_y = {"left": [23, 24, 25, 26],
                   "right": [ 3,  4,  5, 6]}
        
        #Create Entries
        for side in entries_y.keys():
            for l in entries_y[side]:
                e = Entry(self.agent_id, self, side)
                self.grid.place_agent(e, (entries_x[side], l))
                self.schedule.add(e)
                self.entries[side].append(e)
                self.agent_id += 1
                
        #Create Exits
        for side in exits_y.keys():
            for l in exits_y[side]:
                e = Exit(self.agent_id, self, side)
                self.grid.place_agent(e, (exits_x[side], l))
                self.schedule.add(e)
                self.exits[side].append(e)
                self.agent_id += 1

        #Create Walls
        for i in (range(width)):
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, 0))
            self.agent_id += 1
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, height-1))
            self.agent_id += 1
        
        for side, x in entries_x.items():
            for i in (range(height)):
                if ((i not in entries_y[side]) and (i not in exits_y[side])) :
                    w = Wall(self.agent_id, self)
                    self.grid.place_agent(w, (x, i))
                    self.agent_id += 1
                    
        self.entries_pos = {"left": numpy.array([g.pos for g in self.entries["left"]]),
                          "right": numpy.array([g.pos for g in self.entries["right"]])}
        
        self.exits_pos = {"left": numpy.array([g.pos for g in self.exits["left"]]),
                  "right": numpy.array([g.pos for g in self.exits["right"]])}

    def step(self):
        self.entry_rates["left"] = self.leftRateSlider.value
        self.entry_rates["right"] = self.rightRateSlider.value
        self.removals = []
        self.schedule.step()