########
#IMPORTS
########

import random
import numpy
import math

from mesa       import Agent, Model
from mesa.time  import RandomActivation
from mesa.space import MultiGrid

########################
#FUNCTIONS AND VARIABLES
########################

speeds = numpy.arange(0.40, 0.95, 0.05)

#Manhattan Distance
def manhattan_dist(pos_a, pos_b):
    """
    Compute Manhattan Distance in a grid enviroment.
    """
    return(abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1]))

#Octile Distance
def chebyshev_dist(pos_a, pos_b):
    """
    Compute Chebyshev Distance in a grid enviroment.
    """
    return(max([abs(pos_a[0] - pos_b[0]), abs(pos_a[1] - pos_b[1])]))

#Possible moves
def get_possible_moves(player, model):
    """
    Return all possible moves of a given player 
    """
    neighbor_cells = model.grid.get_neighborhood(
        player.pos,
        moore=model.moore_neighborhood,
        include_center=True)
    
    random.shuffle(neighbor_cells)
    distance_to_my_flag = chebyshev_dist(player.pos, model.flag_pos[player.team])
    
    neighbor_cells = [nc for nc in neighbor_cells 
                      if (chebyshev_dist(nc, model.flag_pos[player.team]) > min(1, distance_to_my_flag-1)
                            or model.team_flag[player.team].whogotme)]

    for neighbor in model.grid.neighbor_iter(player.pos, moore = model.moore_neighborhood):
        if isinstance(neighbor, Player) and (neighbor.pos in neighbor_cells):
            neighbor_cells.remove(neighbor.pos)
    
    return neighbor_cells

#Update Orientation
def update_orientation(player, next_pos):
    player.orientation = (next_pos[0] - player.pos[0], next_pos[1] - player.pos[1])
    
#Nearest Agent
def get_nearest_agent(agent, list_of_agents):
    """
    Take as input an agent and a list of other agents
    Return the agent in this list which is the nearest one from the given agent.
    """
    distances = [manhattan_dist(agent.pos, ag.pos) for ag in list_of_agents]
    distances = numpy.array(distances)
    return(list_of_agents[distances.argmin()])
    

#--------------------
#Attack Flag Behavior

def capture_flag(player, model):
    """
    Return all possible of a given player 
    """
    
    possible_moves = get_possible_moves(player, model)
    distances = numpy.zeros(len(possible_moves))
    
    for index, ps in enumerate(possible_moves):
        distances[index] = manhattan_dist(model.flag_pos[(player.team + 1) % 2], ps)
        if ps == player.pos: distances[index] += 1 #If I can't move closer, I can move farther 

    new_position = possible_moves[distances.argmin()]  
    
    if (new_position != player.pos):
        update_orientation(player, new_position)
        model.grid.move_agent(player, new_position)
    
    #Check if i got the flag
    for agent in model.grid.neighbor_iter(player.pos):
        if (isinstance(agent, Flag) 
            and agent.team != player.team 
            and agent.whogotme == None):
                agent.whogotme = player
                player.flag = agent
                player.flag_wait = True


def deliver_flag(player, model):
    """
    This bahavior is used to deliver the opponent's flag to any allied delivery zone.
    """
    possible_moves = get_possible_moves(player, model)
    distances = numpy.zeros(len(possible_moves))
    
    for index, ps in enumerate(possible_moves):
        distances[index] = numpy.array([manhattan_dist(d, ps) for d in model.delivery_pos[player.team]]).min()
        if ps == player.pos: distances[index] += 1 
    
    new_position = possible_moves[distances.argmin()]
    if (new_position != player.pos):
        player.orientation = (new_position[0] - player.pos[0], new_position[1] - player.pos[1])
        model.grid.move_agent(player, new_position)
        model.grid.move_agent(player.flag, new_position)
        model.flag_pos[(player.team + 1) % 2] = new_position
        player.flag_wait = True

def attack_flag(player, model):
    
    if player.flag == None:
            capture_flag(player, model)
    else:
        if player.flag_wait:
            player.flag_wait = False
        else:
            deliver_flag(player, model)

#--------------------
#Defend Flag Behavior
        
def patrol_flag():
    pass

def rescue_flag():
    pass

def defend_flag(player, model):
    pass

#--------------------
#Rescue ally behavior
def rescue_ally(player, model):    
    """
    Rescue an arrested ally 
    """

    arrested_allies = [jail.prisoner for jail in model.team_jails[(player.team + 1) % 2] if jail.prisoner]
    nearest_arrested_ally = get_nearest_agent(player, arrested_allies)
    
    possible_moves = get_possible_moves(player, model)
    distances = numpy.zeros(len(possible_moves))
        
    for index, ps in enumerate(possible_moves):
        distances[index] = manhattan_dist(nearest_arrested_ally.pos, ps)
        if ps == player.pos: distances[index] += 1 #If I can't move closer, I can move farther 

    new_position = possible_moves[distances.argmin()]  
    
    if (new_position != player.pos):
        update_orientation(player, new_position)
        model.grid.move_agent(player, new_position)
    
    #Check if i reached the arrested ally
    for agent in model.grid.neighbor_iter(player.pos):
        if (isinstance(agent, Player) 
            and agent.team == player.team
            and agent.arrested_in):
                agent.arrested_in.prisoner = None
                agent.arrested_in = None

#---------------------
#Attack enemy bahavior
def attack_enemy(player, model):
    neighbors = [neighbor for neighbor in model.grid.neighbor_iter(player.pos)]
    if neighbors:
        agent = random.choice(neighbors)
        if (isinstance(agent, Player) 
            and agent.team != player.team 
            and not agent.arrested_in):
                empty_jails = [jail for jail in model.team_jails[player.team] if not jail.prisoner]
                if empty_jails:
                    jail = random.choice(empty_jails)
                    model.grid.move_agent(agent, jail.pos)
                    jail.prisoner = agent
                    agent.arrested_in = jail
                    agent.action = "none"
                    if agent.flag:
                        agent.flag.whogotme = None
                        agent.flag = None

#######
#AGENTS
#######
    
#-------------
#Agent: Player
class Player(Agent):
    
    def __init__(self, unique_id, model, team, orientation):
        super().__init__(unique_id, model)
        self.team = team
        self.orientation = orientation
        self.flag = None
        self.arrested_in = None
        self.action = "none"
        
    def step(self):
        
        allies_actions = [ally.action for ally in self.model.team_players[self.team]]
        
        nearest_opponent = get_nearest_agent(self, self.model.team_players[(self.team + 1) % 2])
        allies_arrested = [jail.prisoner for jail in self.model.team_jails[(self.team + 1) % 2] if jail.prisoner]
        
        if self.arrested_in:
            pass
        elif (len(allies_arrested) > 0 and (("rescue" not in allies_actions) or self.action == "rescue")):
            rescue_ally(self, self.model)
            self.action = "rescue"
        elif (manhattan_dist(self.pos, nearest_opponent.pos) < 2):
            attack_enemy(self, self.model)
            self.action = "attack_enemy"
        elif True:
            attack_flag(self, self.model)
            self.action = "attack_flag"
        else:
            defend_flag(self, self.model)
            self.action = "defend_flag"
            

#-----------
#Agent: Flag
class Flag(Agent):
    
    def __init__(self, unique_id, model, team):
        super().__init__(unique_id, model)
        self.team = team
        self.whogotme = None
        
    def step(self):
        if self.pos in self.model.delivery_pos[(self.team + 1) % 2]:
            self.model.grid.move_agent(self, self.model.init_flag_pos[self.team])
            self.whogotme.flag = None
            self.whogotme = None
            self.model.flag_pos[self.team] = self.pos
    
#-----------
#Agent: Jail
class Jail(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.prisoner = None
        
    def step(self):
        pass
    
#---------------
#Agent: Delivery
class Delivery(Agent):
    
    def __init__(self, unique_id, model, team):
        super().__init__(unique_id, model)
        self.team = team
        
    def step(self):
        pass
    
######
#MODEL
######



class CaptureFlag(Model):
    """
    Capture the Flag:
    There are two teams.
    Each gate has 
    """
    
    def __init__(self, width, height):
        self.grid = MultiGrid(width, height, False)
        
        #Parameters
        self.njails = 5
        self.nplayers = 2*3
        self.delivery_area = 5
        self.moore_neighborhood = False
        
        self.schedule = RandomActivation(self)
        self.running = True

        self.agent_id = 0
        
        #-----
        #Setup
        
        #Flag position
        self.init_flag_pos = [(3, math.floor(height/2)), (width - 4, math.floor(height/2))]
        self.flag_pos = [(3, math.floor(height/2)), (width - 4, math.floor(height/2))]
        
        #Init team positioning
        self.team_positioning = [
                [(6, math.floor(height/2) + math.floor(self.delivery_area/2) - 2*idx + math.floor(self.nplayers/2)) for idx in range(self.nplayers)],
                [(width - 7, math.floor(height/2) + math.floor(self.delivery_area/2) - 2*idx + math.floor(self.nplayers/2)) for idx in range(self.nplayers)]]
        self._init_players_orientation = [(1, 0), (-1, 0)]
        
        #Deliveries positioning        
        self.delivery_pos = [
                [(0, math.floor(height/2) + math.floor(self.delivery_area/2) - idx) for idx in range(self.delivery_area)],
                [(width-1, math.floor(height/2) + math.floor(self.delivery_area/2) - idx) for idx in range(self.delivery_area)]]
        
        #Jails positioning
        self.jails_positioning = [
                [(math.floor(width/2) - math.floor(self.njails/2) + idx, 0) for idx in range(self.njails)],
                [(math.floor(width/2) - math.floor(self.njails/2) + idx, height-1) for idx in range(self.njails)]]
        
        #Current prisoners
        self.prisoners = [[], []]
        
        #List to store team players
        self.team_players = [[], []]
        self.team_deliveries = [[], []]
        self.team_jails = [[], []]
        self.team_flag = []
        
        
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
                p = Player(self.agent_id, self, team, self._init_players_orientation[team])
                self.team_players[team].append(p)
                self.grid.place_agent(p, pos)
                self.schedule.add(p)
                self.agent_id += 1
        
            #Delivery
            for pos in self.delivery_pos[team]:
                d = Delivery(self.agent_id, self, team)
                self.team_deliveries[team].append(d)
                self.grid.place_agent(d, pos)
                self.schedule.add(d)
                self.agent_id += 1
            
            #Jails
            for pos in self.jails_positioning[team]:
                j = Jail(self.agent_id, self)
                self.team_jails[team].append(j)
                self.grid.place_agent(j, pos)
                self.schedule.add(j)
                self.agent_id += 1  
    
    def step(self):
        self.schedule.step()