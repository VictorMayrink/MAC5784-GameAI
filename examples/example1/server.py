# model.py
from model      import MoneyModel

# run.py
model = MoneyModel(50, 10, 10)
for i in range(20):
    model.step()
  

import matplotlib.pyplot as plt   
import numpy as np

agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
plt.imshow(agent_counts, interpolation='nearest')
plt.colorbar()

# If running from a text editor or IDE, remember you'll need the following:
plt.show()
