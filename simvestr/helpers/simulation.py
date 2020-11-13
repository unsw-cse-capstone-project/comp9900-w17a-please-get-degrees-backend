# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 14:10:56 2020

@author: Kovid
"""
import datetime
import time
from math import ceil
from datetime import timedelta

from simvestr.helpers.portfolio import calculate_all_portfolios_values


def update_portfolio(duration: timedelta, interval: timedelta, app, new_day=False):
    duration_s = duration.total_seconds()
    interval_s = interval.total_seconds()
    n_iter = ceil(duration_s / interval_s)
    next_day = None
    today = datetime.datetime.today()
    if new_day:
        next_day = today

    with app.app_context():
        while duration_s >= 0:
            time.sleep(interval_s)
            duration_s -= interval_s
            n_iter -= 1
            if new_day:
                next_day += datetime.timedelta(days=1)
            calculate_all_portfolios_values(new_day=next_day)

            print(f'Portfolio updated {n_iter}')
            '''
                21600 =  6 hours   
                43200 = 12 hours
                86400 = 24 hours
            '''
    print("Simulation complete")
