########
#IMPORTS
########

import sys
sys.path.insert(0, "./")

from projects.flag.model import CaptureFlag
from projects.flag.model import Delivery
from projects.flag.model import Player
from projects.flag.model import Flag
from projects.flag.model import Jail
from projects.flag.model import Wall

from mesa.visualization.modules   import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

########################
#FUNCTIONS AND VARIABLES
########################

flag_colors = ["blue", "red"]
player_colors = ["blue", "red"]
delivery_colors = ["#D46A6A", "#5B8CC3"]

###########
#PORTRAYALS
###########

def agent_portrayal(agent):
    
    if (type(agent) == Player):
        portrayal = {"Shape": "arrowHead",
                     "Filled": "true",
                     "scale": 0.5,
                     "heading_x": agent.orientation[0],
                     "heading_y": agent.orientation[1],
                     "Layer": 3,
                     "Color": player_colors[agent.team]}
    
    elif (type(agent) == Jail):
        portrayal = {"Shape": "rect",
             "Filled": "true",
             "Color": "gray",
             "Layer": 2,
             "w": 1,
             "h": 1}
    
    elif (type(agent) == Flag):      
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Color": flag_colors[agent.team],
                     "Layer": 1,
                     "r": 0.7}
        
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