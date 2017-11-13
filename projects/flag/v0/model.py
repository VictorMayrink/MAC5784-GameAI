########
#IMPORTS
########

import sys
sys.path.insert(0, "./")

import random
import numpy
import math

import influence_masks as im
import patrolling as pt

from mesa       import Agent, Model
from mesa.time  import RandomActivation
from mesa.space import MultiGrid
from astar      import AStar

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

########################
#FUNCTION: Possibe moves
########################
def possible_moves(player, pos):
    """
    Return all possible moves of a given player 
    """
    neighbor_cells = player.model.grid.get_neighborhood(
        pos,
        moore=player.model.moore_neighborhood,
        include_center=True)

    for neighbor in player.model.grid.neighbor_iter(pos, moore = player.model.moore_neighborhood):
        if ((isinstance(neighbor, Wall) or
            isinstance(neighbor, Player) or
            isinstance(neighbor, FireShot) or
            (isinstance(neighbor, Flag) and neighbor.team == player.team)) and
            (neighbor.pos in neighbor_cells)):
               neighbor_cells.remove(neighbor.pos)
    
    return neighbor_cells

#############################
#FUNCTION: Update Orientation
#############################
def update_orientation(player, next_pos):
    player.orientation = (next_pos[0] - player.pos[0], next_pos[1] - player.pos[1])
    
#################################
#FUNCTION: Find the nearest agent
#################################
def get_nearest_agent(agent, list_of_agents):
    """
    Take as input an agent and a list of other agents
    Return the agent in this list which is the nearest one from the given agent.
    """
    distances = [manhattan_dist(agent.pos, ag.pos) for ag in list_of_agents]
    distances = numpy.array(distances)
    return(list_of_agents[distances.argmin()])

#########################
#CLASS: AStar Path Finder
#########################
class AStarSolver(AStar):

    """
    Use the AStar algorithm to find the best path to a desired position.
    """

    def __init__(self, player):
        self.player = player

    def heuristic_cost_estimate(self, n1, n2):
        """Computes the 'octile' distance between two (x,y) tuples"""
        return diagonal_dist(n1, n2)

    def distance_between(self, n1, n2):
        """This method always returns the cost to move to an adjacent cell"""
        return(im.get_inf_value(self.player.model.playermap, n2) +
               im.get_inf_value(self.player.model.firemap, n2))

    def neighbors(self, node):
        """ 
        For a given coordinate in the grid, returns up to 8 adjacent nodes
            (north, east, south, west, north-east, north-west, south-east, south-west)
            that can be reached from the current position
        """
        return possible_moves(self.player, node)


####################
#CLASS: Player Agent
####################
class Player(Agent):
     
    def __init__(self, unique_id, model, team, orientation, position):
        super().__init__(unique_id, model)
        self.team = team
        self.speed = 0.5
        self.orientation = orientation
        self.flag = None
        self.action = None
        self.lock_countdown = 0
        self.pathfinder = AStarSolver(self)
        self.cover_positions = list(2*numpy.array([(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)], dtype = numpy.uint8))
        self.model.grid.place_agent(self, position)
        self.model.playermap = im.sum_inf_mask(self.model.playermap, im.player_inf_mask, self.pos)

    #------------------------->
    #Move to the next position>
    def move(self, next_move):        
        self.model.playermap = im.sum_inf_mask(self.model.playermap, -im.player_inf_mask, self.pos)        
        self.orientation = (next_move[0] - self.pos[0], next_move[1] - self.pos[1])
        self.model.grid.move_agent(self, next_move)        
        self.model.playermap = im.sum_inf_mask(self.model.playermap, im.player_inf_mask, self.pos)        
        if self.flag: self.model.grid.move_agent(self.flag, self.pos)
    #Move to the next position<
    #-------------------------<

    #-------------------->
    #Attack Flag Behavior>
    def capture_flag(self):
        path = self.pathfinder.astar(self.pos, self.model.team_flag[(self.team + 1) % 2].pos)
        if path:
            path = list(path)
            if len(path) > 1: self.move(path[1])        
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for agent in cell_contents:
            if isinstance(agent, Flag) and (agent.team != self.team):
                self.flag = agent
                self.flag.player = self
    
    def deliver_flag(self):
        path = self.pathfinder.astar(self.pos, self.model.team_deliveries[self.team][2].pos)
        if path:
            path = list(path)
            self.move(path[1])
            
    def cover(self, player_with_enemy_flag):
        pmoves = possible_moves(self, self.pos)
        distances = numpy.array([manhattan_dist(player_with_enemy_flag.pos, pm) for pm in pmoves])       
        new_position = pmoves[distances.argmin()]
        self.move(new_position)

    
    def attack_flag(self):        
        player_with_enemy_flag = self.model.team_flag[(self.team + 1) % 2].player        
        if player_with_enemy_flag:
            if self.flag:
                self.deliver_flag()
            else:
                self.cover(player_with_enemy_flag)
        else:
            print("capture")
            self.capture_flag()
    #Attack Flag Behavior<
    #--------------------<
    
    #-------------------->
    #Should fire function>
    def should_fire(self):
        pass
    #Should fire function<        
    #--------------------<
    
    def shoot_at_flag(self):
        target_vec = numpy.subtract(self.model.team_flag[self.team].pos, self.pos)
        inner_prod = numpy.inner(target_vec, self.model.neighborhood_norm)
        self.orientation = self.model.neighborhood[inner_prod.argmax()]
        self.fire()        
    
    #------------->
    #Fire Behavior>
    def fire(self):
        print(self.orientation)
        fs = FireShot(self.model.agent_id, self.model, self.orientation, self.pos)
        self.model.schedule.add(fs)
        self.model.agent_id += 1
    #Fire Behavior<
    #-------------<

    #-------------------->
    #Defend Flag Behavior>
    def patrol_flag(self):    
        patrol_contour_position = tuple(numpy.subtract(self.pos, self.model.team_flag[self.team].pos))
        patrol_contour_position = pt.patrol_positions[patrol_contour_position]
        delta = pt.patrol_contour[patrol_contour_position+1] if patrol_contour_position < 15 else pt.patrol_contour[0]
        new_position = (self.model.team_flag[self.team].pos[0] + delta[0],
                        self.model.team_flag[self.team].pos[1] + delta[1])
        neighbors = [neighbor for neighbor in self.model.grid.get_cell_list_contents(new_position) if not isinstance(neighbor, Delivery)]
        if not neighbors: self.move(new_position)
            
    def rescue_flag(self):    
        pmoves = possible_moves(self, self.pos)
        distances = numpy.zeros(len(pmoves))        
        for index, pm in enumerate(pmoves):
            distances[index] = manhattan_dist(self.model.flag_pos[self.team], pm)
            if pm == self.pos: distances[index] += 1 #If I can't move closer, I can move farther 
        new_position = pmoves[distances.argmin()]  
        if (new_position != self.pos): self.move(new_position)
            
    def go_to_flag(self):    
        pmoves = possible_moves(self, self.pos)
        patrol_cells = numpy.add(self.model.team_flag[self.team].pos, pt.patrol_contour)
        distances = numpy.zeros(len(pmoves))        
        for index, pm in enumerate(pmoves):
            distances[index] = numpy.array([manhattan_dist(pc, pm) for pc in patrol_cells]).min()
            if pm == self.pos: distances[index] += 1        
        new_position = pmoves[distances.argmin()]
        if (new_position != self.pos): self.move(new_position)
            
    def defend_flag(self):
        if self.model.team_flag[self.team].player:
            #self.rescue_flag()
            if random.random() > 0.7:
                self.shoot_at_flag()
            else:
                self.go_to_flag()
        elif chebyshev_dist(self.pos, self.model.team_flag[self.team].pos) == 2:
            self.patrol_flag()
        else:
            self.go_to_flag()
    #Defend Flag Behavior<       
    #--------------------<
    
    def step(self):
        if self.lock_countdown > 0:
            self.lock_countdown -= 1
        elif random.random() < self.speed:
            if self.action == "attack_flag":
                self.attack_flag()
            else:
                self.defend_flag()
            

##################
#CLASS: Flag Agent
##################
class Flag(Agent):
    
    def __init__(self, unique_id, model, team):
        super().__init__(unique_id, model)
        self.team = team
        self.player = None
        
    def respawn(self):
        self.model.grid.move_agent(self, self.model.init_flag_pos[self.team])
        
    def step(self):
        if self.pos in self.model.delivery_pos[(self.team + 1) % 2]:
            self.player.flag = None
            self.player = None
            self.respawn()

##################
#CLASS: Jail Agent
##################
class FireShot(Agent):
    
    def __init__(self, unique_id, model, orientation, position):
        super().__init__(unique_id, model)
        self.orientation = orientation
        self.travelled_dist = 0
        self.crashed = False
        self.model.grid.place_agent(self, position)
        self.model.firemap = im.sum_inf_mask(self.model.firemap, im.fs_inf_mask[self.orientation], self.pos)
    
    def go(self):
        self.travelled_dist += 1
        next_move = tuple(numpy.add(self.pos, self.orientation))
        self.model.firemap = im.sum_inf_mask(self.model.firemap, -im.fs_inf_mask[self.orientation], self.pos)
        self.model.grid.move_agent(self, next_move)
        self.model.firemap = im.sum_inf_mask(self.model.firemap, im.fs_inf_mask[self.orientation], self.pos)
    
    def crash(self):
        self.crashed = True
        self.model.firemap = im.sum_inf_mask(self.model.firemap, -im.fs_inf_mask[self.orientation], self.pos)
    
    def step(self):        
        if self.unique_id not in self.model.removals:
            
            if self.crashed:
                self.model.grid._remove_agent(self.pos, self)
                self.model.schedule.remove(self)
                self.model.removals.append(self.unique_id)
            else:
                self.go()
                
                next_cell_contents = self.model.grid.get_cell_list_contents(self.pos)
                
                for agent in next_cell_contents:
                    if isinstance(agent, Wall):
                        self.crash()
                    elif isinstance(agent, Player):
                        self.crash()
                        agent.lock_countdown = 4
                        if agent.flag:
                            agent.flag.player = None
                            self.model.grid.move_agent(agent.flag, (agent.pos[0] - agent.orientation[0], agent.pos[1] - agent.orientation[1]))
                            agent.flag = None
                        
                #Remove fireshot after a long travelled distance
                if self.travelled_dist > 100:
                    self.model.grid._remove_agent(self.pos, self)
                    self.model.schedule.remove(self)
                    self.model.removals.append(self.unique_id)
    
############################
#CLASS: Delivery Point Agent
############################
class Delivery(Agent):
    
    def __init__(self, unique_id, model, team):
        super().__init__(unique_id, model)
        self.team = team
        
    def step(self):
        pass

##################
#CLASS: Wall Agent
##################
class Wall(Agent):
    """An agent that restrict Walker movements"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def step(self):
        pass

############################################
#CLASS: Capture the Flag - Agent Based model
############################################
class CaptureFlag(Model):
    """
    Capture the Flag:
    """
    
    def __init__(self, width, height):
        self.grid = MultiGrid(width, height, False)
        
        #Parameters
        self.njails = 5
        self.nplayers = 4
        self.delivery_area = 5
        self.moore_neighborhood = True
        self.removals = []
        self.padding = 2*10
        
        self.schedule = RandomActivation(self)
        self.running = True

        self.agent_id = 0
        
        self.neighborhood = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(-1,1),(1,-1)]
        self.neighborhood_norm = numpy.array(self.neighborhood) / numpy.linalg.norm(self.neighborhood, axis = 1)[:,None]
        
        #--------------
        #Influence maps
        self.firemap = numpy.ones((height, width), dtype = int)
        self.playermap = numpy.ones((height, width), dtype = int)
        
        #-----
        #Setup
        
        #Flag position
        self.init_flag_pos = [(4, math.floor(height/2)), (width - 5, math.floor(height/2))]
        self.flag_pos = [(3, math.floor(height/2)), (width - 4, math.floor(height/2))]
        
        #Init team positioning
        self.team_positioning = [
                [(self.flag_pos[0][0]+3, self.flag_pos[0][1] + 2*k+1) for k in range(-self.nplayers, self.nplayers)],
                [(self.flag_pos[1][0]-3, self.flag_pos[1][1] + 2*k+1) for k in range(-self.nplayers, self.nplayers)]
                ]
        self._init_players_orientation = [(1, 0), (-1, 0)]
        
        #Deliveries positioning        
        self.delivery_pos = [
                [(1, math.floor(height/2) + math.floor(self.delivery_area/2) - idx) for idx in range(self.delivery_area)] +
                [(2, math.floor(height/2) + math.floor(self.delivery_area/2) - idx) for idx in range(1,self.delivery_area-1)],
                [(width-2, math.floor(height/2) + math.floor(self.delivery_area/2) - idx) for idx in range(self.delivery_area)] +
                [(width-3, math.floor(height/2) + math.floor(self.delivery_area/2) - idx) for idx in range(1,self.delivery_area-1)]]
                
        #List to store team players
        self.team_players = [[], []]
        self.team_deliveries = [[], []]
        self.team_flag = []
        
        #Create Walls
        for i in range(width):
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, 0))
            self.agent_id += 1
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (i, height-1))
            self.agent_id += 1
            
        for i in range(1, height - 1):
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (0, i))
            self.agent_id += 1
            w = Wall(self.agent_id, self)
            self.grid.place_agent(w, (width-1, i))
            self.agent_id += 1
        
        #Populate Teams
        for team in [0, 1]:
            #Flag
            f = Flag(self.agent_id, self, team)
            self.team_flag.append(f)
            self.grid.place_agent(f, self.init_flag_pos[team])
            self.schedule.add(f)
            self.agent_id += 1
        
            #Players
            for pos in self.team_positioning[team]:
                p = Player(self.agent_id, self, team, self._init_players_orientation[team], pos)
                self.team_players[team].append(p)
                self.schedule.add(p)
                self.agent_id += 1
        
            #Delivery
            for pos in self.delivery_pos[team]:
                d = Delivery(self.agent_id, self, team)
                self.team_deliveries[team].append(d)
                self.grid.place_agent(d, pos)
                self.schedule.add(d)
                self.agent_id += 1
                
        numpy.savetxt("infmap.csv", self.playermap,  delimiter=",")
        self.team_players[0][0].action = "attack_flag"
        self.team_players[0][1].action = "attack_flag"
        self.team_players[1][0].action = "attack_flag"
        self.team_players[1][1].action = "attack_flag"
    
    def step(self):
        self.schedule.step()
        self.removals = []
        numpy.savetxt("infmap.csv", self.playermap,  delimiter=",", fmt = "%.2d")