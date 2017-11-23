import sys
sys.path.insert(0, "./")

import numpy

from projects.flag.model import CaptureFlag

width = 40
height = 27

models = [
        CaptureFlag(width, height, 1, 1),
        CaptureFlag(width, height, 2, 1),
        CaptureFlag(width, height, 3, 1),
        CaptureFlag(width, height, 4, 1),
        CaptureFlag(width, height, 5, 1),
        CaptureFlag(width, height, 6, 1),
        CaptureFlag(width, height, 7, 1),
        
        CaptureFlag(width, height, 1, 2),
        CaptureFlag(width, height, 2, 2),
        CaptureFlag(width, height, 3, 2),
        CaptureFlag(width, height, 4, 2),
        CaptureFlag(width, height, 5, 2),
        CaptureFlag(width, height, 6, 2),
        CaptureFlag(width, height, 7, 2),
        
        CaptureFlag(width, height, 1, 3),
        CaptureFlag(width, height, 2, 3),
        CaptureFlag(width, height, 3, 3),
        CaptureFlag(width, height, 4, 3),
        CaptureFlag(width, height, 5, 3),
        CaptureFlag(width, height, 6, 3),
        CaptureFlag(width, height, 7, 3),
        
        CaptureFlag(width, height, 1, 4),
        CaptureFlag(width, height, 2, 4),
        CaptureFlag(width, height, 3, 4),
        CaptureFlag(width, height, 4, 4),
        CaptureFlag(width, height, 5, 4),
        CaptureFlag(width, height, 6, 4),
        CaptureFlag(width, height, 7, 4),
        
        CaptureFlag(width, height, 1, 5),
        CaptureFlag(width, height, 2, 5),
        CaptureFlag(width, height, 3, 5),
        CaptureFlag(width, height, 4, 5),
        CaptureFlag(width, height, 5, 5),
        CaptureFlag(width, height, 6, 5),
        CaptureFlag(width, height, 7, 5),
        
        CaptureFlag(width, height, 1, 6),
        CaptureFlag(width, height, 2, 6),
        CaptureFlag(width, height, 3, 6),
        CaptureFlag(width, height, 4, 6),
        CaptureFlag(width, height, 5, 6),
        CaptureFlag(width, height, 6, 6),
        CaptureFlag(width, height, 7, 6),
        
        CaptureFlag(width, height, 1, 7),
        CaptureFlag(width, height, 2, 7),
        CaptureFlag(width, height, 3, 7),
        CaptureFlag(width, height, 4, 7),
        CaptureFlag(width, height, 5, 7),
        CaptureFlag(width, height, 6, 7),
        CaptureFlag(width, height, 7, 7)
        ]

for i in range(5000):
    print(i)
    for m in range(len(models)):
        models[m].step()

results_tbl_blue = numpy.array([
        [models[0].scoreboard[0], models[ 7].scoreboard[0], models[14].scoreboard[0], models[21].scoreboard[0], models[28].scoreboard[0], models[35].scoreboard[0], models[42].scoreboard[0]],
        [models[1].scoreboard[0], models[ 8].scoreboard[0], models[15].scoreboard[0], models[22].scoreboard[0], models[29].scoreboard[0], models[36].scoreboard[0], models[43].scoreboard[0]],
        [models[2].scoreboard[0], models[ 9].scoreboard[0], models[16].scoreboard[0], models[23].scoreboard[0], models[30].scoreboard[0], models[37].scoreboard[0], models[44].scoreboard[0]],
        [models[3].scoreboard[0], models[10].scoreboard[0], models[17].scoreboard[0], models[24].scoreboard[0], models[31].scoreboard[0], models[38].scoreboard[0], models[45].scoreboard[0]],
        [models[4].scoreboard[0], models[11].scoreboard[0], models[18].scoreboard[0], models[25].scoreboard[0], models[32].scoreboard[0], models[39].scoreboard[0], models[46].scoreboard[0]],
        [models[5].scoreboard[0], models[12].scoreboard[0], models[19].scoreboard[0], models[26].scoreboard[0], models[33].scoreboard[0], models[40].scoreboard[0], models[47].scoreboard[0]],
        [models[6].scoreboard[0], models[13].scoreboard[0], models[20].scoreboard[0], models[27].scoreboard[0], models[34].scoreboard[0], models[41].scoreboard[0], models[48].scoreboard[0]]
        ])
    
results_tbl_red = numpy.array([
        [models[0].scoreboard[1], models[ 7].scoreboard[1], models[14].scoreboard[1], models[21].scoreboard[1], models[28].scoreboard[1], models[35].scoreboard[1], models[42].scoreboard[1]],
        [models[1].scoreboard[1], models[ 8].scoreboard[1], models[15].scoreboard[1], models[22].scoreboard[1], models[29].scoreboard[1], models[36].scoreboard[1], models[43].scoreboard[1]],
        [models[2].scoreboard[1], models[ 9].scoreboard[1], models[16].scoreboard[1], models[23].scoreboard[1], models[30].scoreboard[1], models[37].scoreboard[1], models[44].scoreboard[1]],
        [models[3].scoreboard[1], models[10].scoreboard[1], models[17].scoreboard[1], models[24].scoreboard[1], models[31].scoreboard[1], models[38].scoreboard[1], models[45].scoreboard[1]],
        [models[4].scoreboard[1], models[11].scoreboard[1], models[18].scoreboard[1], models[25].scoreboard[1], models[32].scoreboard[1], models[39].scoreboard[1], models[46].scoreboard[1]],
        [models[5].scoreboard[1], models[12].scoreboard[1], models[19].scoreboard[1], models[26].scoreboard[1], models[33].scoreboard[1], models[40].scoreboard[1], models[47].scoreboard[1]],
        [models[6].scoreboard[1], models[13].scoreboard[1], models[20].scoreboard[1], models[27].scoreboard[1], models[34].scoreboard[1], models[41].scoreboard[1], models[48].scoreboard[1]]
        ])