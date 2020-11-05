# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 14:10:56 2020

@author: Kovid
"""

import time
from simvestr.helpers.portfolio import calculate_all_portfolios_values
    
def update_portfolio():
    for _ in range(10):
        # calculate_all_portfolios_values()
        print('Portfolio updated')
        '''
            21600 =  6 hours   
            43200 = 12 hours
            86400 = 24 hours
        '''
        time.sleep(2)