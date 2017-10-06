# -*- coding:utf-8 -*-
"""Monte Carlo Tree Search solution for Gomoku"""

import math




def uct(wi, ni, t, c=math.sqrt(2)):
    """Upper Confidence bound for Trees
    wi: number of wins
    ni: number of simulations
    c: exploration parameter
    t: total number of simulations(sum of ni)"""
    return wi/ni + c * math.sqrt(math.log(t)/ni)
