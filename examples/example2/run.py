import numpy as np
import matplotlib.pyplot as plt  

from model import MoneyModel, compute_gini

model = MoneyModel(100, 10, 10)
for i in range(100):
    model.step()

#Plot heatmap with number of agents in each position
agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
plt.imshow(agent_counts, interpolation='nearest')
plt.colorbar()
plt.show()

#Plot Gini coefficients
gini = model.datacollector.get_model_vars_dataframe()
gini.plot()

#Data frame with agen wealth at each step
agent_wealth = model.datacollector.get_agent_vars_dataframe()
agent_wealth.head()

#Histogram of agent's wealth
end_wealth = agent_wealth.xs(99, level="Step")["Wealth"]
end_wealth.hist(bins=range(agent_wealth.Wealth.max()+1))

#Plot wealth time series for a given agent (AgentII = 15 in this case)
one_agent_wealth = agent_wealth.xs(15, level="AgentID")
one_agent_wealth.Wealth.plot()

#Batch Runner
from mesa.batchrunner import BatchRunner

fixed_params = {"width": 10,"height": 10}
variable_params = {"N": range(10, 500, 10)}

batch_run = BatchRunner(MoneyModel,
                        fixed_parameters=fixed_params,
                        variable_parameters=variable_params,
                        iterations=5,
                        max_steps=100,
                        model_reporters={"Gini": compute_gini})
batch_run.run_all()

run_data = batch_run.get_model_vars_dataframe()
run_data.head()
plt.scatter(run_data.N, run_data.Gini)