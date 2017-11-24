########
#IMPORTS
########

import sys
sys.path.insert(0, "./")

from projects.metro.unidir.model import MetroModel
from projects.metro.unidir.model import Walker
from projects.metro.unidir.model import Wall
from projects.metro.unidir.model import Entry
from projects.metro.unidir.model import Exit

from mesa.visualization.modules   import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer

#####################################
#FUNCTION: Render agent visualization
#####################################

def agent_portrayal(agent):
        
    if (type(agent) == Walker):
        portrayal = {"Shape": "arrowHead",
                     "Filled": "true",
                     "scale": 0.5,
                     "heading_x": agent.orientation[0],
                     "heading_y": agent.orientation[1],
                     "Layer": 3,
                     "Color": "red" if agent.source == "right" else "blue"}
    
    elif (type(agent) == Wall):
        
        portrayal = {"Shape": "rect",
             "Filled": "true",
             "Color": "black",
             "Layer": 2,
             "w": 1,
             "h": 1}
    
    elif (type(agent) == Entry):
        
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Color": ("#EA7869" if agent.entry_type == "left" else "#8D99A2"),
                     "Layer": 1,
                     "w": 1,
                     "h": 1}
    
    elif (type(agent) == Exit):
        
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Color": ("#8D99A2" if agent.exit_type == "left" else "#EA7869"),
                     "Layer": 1,
                     "w": 1,
                     "h": 1}
        
    return portrayal

##################################
#SETTINGS: global model parameters
##################################
        
width = 45
height = 30
pixels = 17

leftRate_slider = UserSettableParameter("slider", "Left Rate", 0.15, 0, 0.70, 0.01)
rightRate_slider = UserSettableParameter("slider", "Right Rate", 0.15, 0, 0.70, 0.01)

#############################
#MODEL: create model instance
#############################

grid = CanvasGrid(agent_portrayal, width, height, pixels*width, pixels*height)

server = ModularServer(MetroModel,
                       [grid],
                       "Metro Station Model",
                       {"leftRateSlider": leftRate_slider,
                        "rightRateSlider": rightRate_slider,
                        "width": width,
                        "height": height})