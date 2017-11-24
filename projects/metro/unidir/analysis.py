import sys
sys.path.insert(0, "./")

import matplotlib.pyplot as plt
import numpy
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
        MetroModel(width, height, 0.7, 0.7),
        MetroModel(width, height, 0.8, 0.8)
        ]

for i in range(1000):
    print(i)
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
ativcounts = []
for m in range(len(models)):
    ages.append(pd.DataFrame(models[m].walker_ages, columns=['speed', 'age']))
    ages[m]["speedage"] = ages[m].speed * ages[m].age
    dists.append(pd.DataFrame(models[m].walker_ages, columns=['speed', 'dist']))
    ativcounts.append(pd.DataFrame(models[m].walker_atvcounts, columns=['speed', 'atvs']))
    
plt.boxplot([d.dist for d in dists])
plt.grid()
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
plt.xlabel("Fluxo de entrada (ambos os lados)")
plt.ylabel("Distância percorrida")
plt.savefig("./latex/figures/dists_boxplot.png")

plt.boxplot([atv.atvs for atv in ativcounts])
plt.grid()
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
plt.xlabel("Fluxo de entrada (ambos os lados)")
plt.ylabel("Número de ativações")
plt.ylim([43, 60])
plt.savefig("./latex/figures/ativs_boxplot.png")