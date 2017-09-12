import random
import numpy

from mesa       import Agent, Model
from mesa.time  import RandomActivation
from mesa.space import MultiGrid

speeds = numpy.arange(0.40, 0.95, 0.05)

def manhatan_dist(pos_a, pos_b):   
    return(abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1]))

    
class Person(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, source):
        super().__init__(unique_id, model)
        self.speed = random.choice(speeds)
        self.source = source
        
    def move(self):

        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=True)
        random.shuffle(possible_steps)

        for neighbor in  self.model.grid.neighbor_iter(self.pos):
            if ((isinstance(neighbor, Wall) or isinstance(neighbor, Person)) and (neighbor.pos in possible_steps)):
                possible_steps.remove(neighbor.pos)
        
        if self.source == "left":
            distances = numpy.zeros(len(possible_steps))
            for index, ps in enumerate(possible_steps):
                distances[index] = numpy.array([manhatan_dist(g, ps) for g in self.model.rightGates]).min()
        else:
            distances = numpy.zeros(len(possible_steps))
            for index, ps in enumerate(possible_steps):
                distances[index] = numpy.array([manhatan_dist(g, ps) for g in self.model.leftGates]).min()
                
        new_position = possible_steps[distances.argmin()]
        
        self.model.grid.move_agent(self, new_position)
        
    def step(self):
        if self.unique_id not in self.model.removals:
            if (random.random() < self.speed):
                self.move()

class Gate(Agent):
    """An agent that creates and removes persons"""
    def __init__(self, unique_id, model, gate_type):
        super().__init__(unique_id, model)
        self.gate_type = gate_type
    
    def step(self):
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        foreign = [obj for obj in this_cell if (isinstance(obj, Person) and obj.source != self.gate_type)]
        natives = [obj for obj in this_cell if (isinstance(obj, Person) and obj.source == self.gate_type)]
        
        for f in foreign:
            self.model.grid._remove_agent(self.pos, f)
            self.model.schedule.remove(f)
            self.model.removals.append(f.unique_id)
        
        if (len(natives) == 0):
            if (self.gate_type == "left"):
                if (random.random() < self.model.leftRate):
                    p = Person(self.model.agent_id, self.model, self.gate_type)
                    self.model.schedule.add(p)
                    self.model.grid.place_agent(p, self.pos)
                    self.model.agent_id += 1
            else:
                if (random.random() < self.model.rightRate):
                    p = Person(self.model.agent_id, self.model, self.gate_type)
                    self.model.schedule.add(p)
                    self.model.grid.place_agent(p, self.pos)
                    self.model.agent_id += 1
                
    
class Wall(Agent):
    """An agent that restrict person movements"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def step(self):
        pass



class MetroModel(Model):
    """A model with some number of agents."""
    def __init__(self, width, height, leftRate, rightRate):
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.removals = []
        self.leftRate = leftRate
        self.rightRate = rightRate
        self.agent_id = 0
        
        w = width-1
        self.leftGates = [(0, 21), (0, 22), (0, 23), (0, 24), (0, 25), (0, 26)]
        self.leftGatesY = [g[1] for g in self.leftGates]
        self.rightGates = [(w, 3), (w, 4), (w, 5), (w, 6), (w, 7), (w, 8)]
        self.rightGatesY = [g[1] for g in self.rightGates]

        #Create Walls
        for i in (range(width)):
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, 0))
            self.schedule.add(w)
            self.agent_id += 1
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, height-1))
            self.schedule.add(w)
            self.agent_id += 1
         
        for i in (range(height)):
            if (i not in self.leftGatesY):
                w = Wall(self.agent_id, self)
                self.grid.place_agent(w, (0, i))
                self.schedule.add(w)
                self.agent_id += 1
            if (i not in self.rightGatesY):
                w = Wall(self.agent_id, self)
                self.grid.place_agent(w, (width-1, i))
                self.schedule.add(w)
                self.agent_id += 1
        
        #Create Gates
        for i in self.leftGatesY:
            g = Gate(self.agent_id, self, "left")
            self.grid.place_agent(g, (0, i))
            self.schedule.add(g)
            self.agent_id += 1

        for i in self.rightGatesY:
            g = Gate(self.agent_id, self, "right")
            self.grid.place_agent(g, (width-1, i))
            self.schedule.add(g)
            self.agent_id += 1

    def step(self):
        self.removals = []
        self.schedule.step()