#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 16:10:35 2017

@author: victor
"""

patrol_contour = [(2,2),(2,1),(2,0),(2,-1),(2,-2),(1,-2),(0,-2),(-1,-2),
                  (-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,2),(0,2),(1,2)]

patrol_positions = {
        ( 2, 2): 0,
        ( 2, 1): 1,
        ( 2, 0): 2,
        ( 2,-1): 3,
        ( 2,-2): 4,
        ( 1,-2): 5,
        ( 0,-2): 6,
        (-1,-2): 7,
        (-2,-2): 8,
        (-2,-1): 9,
        (-2, 0): 10,
        (-2, 1): 11,
        (-2, 2): 12,
        (-1, 2): 13,
        ( 0, 2): 14,
        ( 1, 2): 15
        }