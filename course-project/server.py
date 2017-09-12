from model import MetroModel
from model import Person
from model import Wall
from model import Gate

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    
    
    if (type(agent) == Person):
        portrayal = {"Shape": "arrowHead",
                     "Filled": "true",
                     "scale": 0.5,
                     "heading_x": 1 if agent.source == "left" else -1,
                     "heading_y": 0,
                     "Layer": 3,
                     "Color": "red" if agent.source == "right" else "blue"}
    
    elif (type(agent) == Wall):
        
        portrayal = {"Shape": "rect",
             "Filled": "true",
             "Color": "black",
             "Layer": 2,
             "w": 1,
             "h": 1}
    
    elif (type(agent) == Gate):
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Color": ("#8D99A2" if agent.gate_type == "left" else "#EA7869"),
                     "Layer": 1,
                     "w": 1,
                     "h": 1}
        
    return portrayal
        

grid = CanvasGrid(agent_portrayal, 40, 30, 750, 400)

leftRate_slider = UserSettableParameter("slider", "Left Rate", 0.35, 0, 1, 0.05)
rightRate_slider = UserSettableParameter("slider", "Right Rate", 0.35, 0, 1, 0.05)

server = ModularServer(MetroModel,
                       [grid],
                       "Money Model",
                       {"leftRate": leftRate_slider,
                        "rightRate": rightRate_slider,
                        "width": 40,
                        "height": 30})