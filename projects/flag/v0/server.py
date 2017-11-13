########
#IMPORTS
########

import sys
sys.path.insert(0, "./")

from projects.flag.v0.model import CaptureFlag
from projects.flag.v0.model import Delivery
from projects.flag.v0.model import Player
from projects.flag.v0.model import Flag
from projects.flag.v0.model import Wall
from projects.flag.v0.model import FireShot

from mesa.visualization.modules   import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

########################
#FUNCTIONS AND VARIABLES
########################

flag_colors = ["blue", "red"]
player_colors = ["blue", "red"]
delivery_colors = ["#b7d7e8", "#eea29a"]

###########
#PORTRAYALS
###########

def agent_portrayal(agent):
    
    if (type(agent) == Player):
        portrayal = {"Shape": "arrowHead",
                     "Filled": ("true" if agent.lock_countdown == 0 else ""),
                     "scale": 0.5,
                     "heading_x": agent.orientation[0],
                     "heading_y": agent.orientation[1],
                     "Layer": 3,
                     "Color": player_colors[agent.team]}
    
    elif (type(agent) == Flag):      
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Color": flag_colors[agent.team],
                     "Layer": 1,
                     "r": 0.7}
        
    elif (type(agent) == FireShot):
        
        if agent.crashed:
            portrayal = {"Shape": "star",
                         "scale": 0.8,
                         "spikes": 6,
                         "inset": 0.3,
                         "Filled": "true",
                         "Layer": 3,
                         "Color": "yellow"}
        else:
            portrayal = {"Shape": "circle",
                         "Filled": "true",
                         "Color": "black",
                         "Layer": 1,
                         "r": 0.1}
        
    elif (type(agent) == Delivery):      
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Color": delivery_colors[agent.team],
                     "Layer": 1,
                     "w": 1,
                     "h": 1}
        
    elif (type(agent) == Wall):
        
        portrayal = {"Shape": "rect",
             "Filled": "true",
             "Color": "black",
             "Layer": 2,
             "w": 1,
             "h": 1}
        
    return portrayal
        
width = 40
height = 27
pixels = 18

grid = CanvasGrid(agent_portrayal, width, height, pixels*width, pixels*height)

server = ModularServer(CaptureFlag,
                       [grid],
                       "Capture the Flag",
                       {"width": width,
                        "height": height})