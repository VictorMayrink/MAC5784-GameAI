import random
import numpy

from mesa       import Agent, Model
from mesa.time  import RandomActivation
from mesa.space import MultiGrid

def manhatan_dist(pos_a, pos_b):
    return(abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1]))

class Gate(Agent):
    """An agent that creates and removes persons"""
    def __init__(self, unique_id, model, gate_type):
        super().__init__(unique_id, model)
        self.gate_type = gate_type
    
    def step(self):
        print("Step on postion:", self.pos)
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        people = [obj for obj in this_cell if isinstance(obj, Person)]
        print("People:" + str(people))
        if len(people) > 0:
            person_to_remove = random.choice(people)
            print("Removed:", person_to_remove.unique_id)
            self.model.grid._remove_agent(self.pos, person_to_remove)
            self.model.schedule.remove(person_to_remove)
            self.model.removals.append(person_to_remove.unique_id)
    
class Wall(Agent):
    """An agent that restrict person movements"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def step(self):
        pass
    
class Person(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.speed = random.choice(numpy.arange(0.40, 0.95, 0.05))
        self.type = random.choice(["left", "right"])
        
    def move(self):
        
        print("Moving agent: ", self.unique_id)
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=True)

        for neighbor in  self.model.grid.neighbor_iter(self.pos):
            if ((isinstance(neighbor, Wall) or isinstance(neighbor, Person)) and (neighbor.pos in possible_steps)):
                possible_steps.remove(neighbor.pos)
        
        print(possible_steps)
        distances = numpy.zeros(len(possible_steps))
        for index, ps in enumerate(possible_steps):
            if self.type == "left": 
                distances[index] = manhatan_dist((39, 5), ps)
            else:
                distances[index] = manhatan_dist((0, 25), ps)
                
        print(distances)
        
        new_position = possible_steps[distances.argmin()]
        self.model.grid.move_agent(self, new_position)
        
    def step(self):
        if self.unique_id not in self.model.removals:
            #if (numpy.random() < self.speed):
            self.move()


class MetroModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.removals = []

        #Create Walls
        agent_id = 1
        for i in (range(width)):
            w = Wall(agent_id, self)
            self.grid.place_agent(w, (i, 0))
            self.schedule.add(w)
            agent_id += 1
            w = Wall(agent_id, self)
            self.grid.place_agent(w, (i, height-1))
            self.schedule.add(w)
            agent_id += 1
         
        gateApositions = [21, 22, 23, 24, 25, 26]
        gateBpositions = [3, 4, 5, 6, 7, 8]
        for i in (range(height)):
            if (i not in gateApositions):
                w = Wall(agent_id, self)
                self.grid.place_agent(w, (0, i))
                self.schedule.add(w)
                agent_id += 1
            if (i not in gateBpositions):
                w = Wall(agent_id, self)
                self.grid.place_agent(w, (width-1, i))
                self.schedule.add(w)
                agent_id += 1
        
        #Create Gates
        for i in gateApositions:
            g = Gate(agent_id, self, "left")
            self.grid.place_agent(g, (0, i))
            self.schedule.add(g)
            agent_id += 1

        for i in gateBpositions:
            g = Gate(agent_id, self, "right")
            self.grid.place_agent(g, (width-1, i))
            self.schedule.add(g)
            agent_id += 1

        # Create agents
        for i in range(self.num_agents):
            a = Person(agent_id, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = random.randrange(1, self.grid.width-1)
            y = random.randrange(1, self.grid.height-1)
            self.grid.place_agent(a, (x, y))
            agent_id += 1

    def step(self):
        self.removals = []
        self.schedule.step()