import sys
sys.path.insert(0, "./")

import matplotlib.pyplot as plt
import pandas as pd
import cv2

from projects.metro.unidir.model import MetroModel

width = 45
height = 30

models = [
        MetroModel(width, height, 0.1, 0.1),
        MetroModel(width, height, 0.2, 0.2),
        MetroModel(width, height, 0.3, 0.3),
        MetroModel(width, height, 0.4, 0.4),
        MetroModel(width, height, 0.5, 0.5),
        MetroModel(width, height, 0.6, 0.6),
        MetroModel(width, height, 0.7, 0.7)
        ]

for _ in range(1000):
    for m in range(len(models)):
        models[m].step()

plt.imshow(models[3].heatmap[0], cmap='Blues', interpolation='nearest')
plt.savefig('./latex/figures/blues.png')
plt.imshow(models[3].heatmap[1], cmap='Reds', interpolation='nearest')
plt.savefig('./latex/figures/reds.png')

img1 = cv2.imread('./latex/figures/blues.png')
img2 = cv2.imread('./latex/figures/reds.png')

dst = cv2.addWeighted(img1,0.5,img2,0.5,0)
cv2.imwrite('./latex/figures/heatmap.png',dst)

ages = []
dists = []
for m in range(len(models)):
    ages.append(pd.DataFrame(models[m].walker_ages, columns=['speed', 'age']))
    ages[m]["speedage"] = ages[m].speed * ages[m].age
    dists.append(pd.DataFrame(models[m].walker_ages, columns=['speed', 'dist']))
    
plt.boxplot([d.dist for d in dists])
plt.grid()
plt.xticks([1, 2, 3, 4, 5, 6, 7], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
plt.xlabel("Fluxo de entrada (ambos os lados)")
plt.ylabel("Distância percorrida")
plt.savefig("./latex/figures/dist_boxplot.png")