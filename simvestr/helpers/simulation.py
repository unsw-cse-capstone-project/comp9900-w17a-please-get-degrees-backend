# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 14:10:56 2020

@author: Kovid
"""

import time
from simvestr.helpers.portfolio import calculate_all_portfolios_values
    
def update_portfolio():
    # for _ in range(10):
    c = 0
    while True:
        time.sleep(20)
        # calculate_all_portfolios_values()
        c += 1
        
        print(f'Portfolio updated {c}')
        '''
            21600 =  6 hours   
            43200 = 12 hours
            86400 = 24 hours
        '''
