# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 01:08:54 2020

@author: Kovid
"""

from flask_restx import Resource, fields, reqparse, Namespace

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.portfolio import stock_balance
from simvestr.models import db, Transaction
from simvestr.apis.search import StockDetails
from simvestr.apis.portfolio import PortfolioQuery
from simvestr.helpers.portfolio import all_stocks_balance

import requests
import xlsxwriter

api = Namespace(
    "exportfolio",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Additional Feature - Export portfolio",
    title="Simvestr",
    description="Back-end API for exporting portfolio to csv file",
)

def create_csv(user, portfolio_details):
    file_basename = f'{portfolio_details["portfolio_name"]}.xlsx'
    # path = 'simvestr\\helpers\\'
    path = ''
    workbook = xlsxwriter.Workbook(f'{path+file_basename}')
    worksheet = workbook.add_worksheet()
    
    heading_format_1 = workbook.add_format({'bold': True, 'bg_color': '#28B463', 'font_color': 'black'})
    cell_format_1 = workbook.add_format({'bg_color': '#D2B4DE', 'font_color': 'black'})
    
    heading_format_2 = workbook.add_format({'bold': True, 'bg_color': '#2980B9', 'font_color': 'black'})
    cell_format_2 = workbook.add_format({'bg_color': '#F7DC6F', 'font_color': 'black'})
    
    worksheet.write('A1', 'Name', heading_format_1)
    worksheet.write('B1', f'{user.first_name} {user.last_name}', cell_format_1)
    
    worksheet.write('A2', 'Date Joined', heading_format_2)
    worksheet.write('B2', f'{(user.date_joined).date()}', cell_format_2)
    
    worksheet.write('A3', 'Balance', heading_format_1)
    worksheet.write('B3', f'{portfolio_details["balance"]}', cell_format_1)

    worksheet.write('A4', 'Total Value', heading_format_2)
    worksheet.write('B4', f'{portfolio_details["total_value"]}', cell_format_2)
    
    worksheet.write('A5', 'Cash Balance', heading_format_1)
    worksheet.write('B5', f'{portfolio_details["total_value"] + portfolio_details["balance"]}', cell_format_1)
    
    print(f'Name, {user.first_name} {user.last_name}\n')
    print(f'Date Joined, {(user.date_joined).date()}\n')
    print(f'Balance, {portfolio_details["balance"]}\n')
    print(f'Total Value, {portfolio_details["total_value"]}\n')
    
    
    # Add a format. Light red fill with dark red text.
    format1 = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    
    # Add a format. Green fill with dark green text.
    format2 = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    
    stock_heading_format = workbook.add_format({'bold': True, 'bg_color': '#5DADE2', 'font_color': 'black'})
    
    row = 7
    worksheet.write(f'C{row}', 'Stocks', stock_heading_format)
    worksheet.write(f'D{row}', 'Symbol', stock_heading_format)
    worksheet.write(f'E{row}', 'Quantity', stock_heading_format)
    worksheet.write(f'F{row}', 'Quote', stock_heading_format)
    worksheet.write(f'G{row}', 'Value', stock_heading_format)
    
    owned_stocks = portfolio_details["portfolio"]
    

    for symbol, details  in owned_stocks.items():
        print(symbol, details["quantity"], details["quote"], details["value"])
        row += 1
        # worksheet.write(f'C{row}', f'{symbol}', heading_format)
        worksheet.write(f'D{row}', f'{symbol}')
        worksheet.write(f'E{row}', f'{details["quantity"]}')
        worksheet.write(f'F{row}', f'{details["quote"]}', format1)
        worksheet.write(f'G{row}', f'{details["value"]}', format2)
        
        
    workbook.close()

@api.route("")
class ExportPortfolio(Resource):
    @api.response(200, "Successful")
    @requires_auth
    def get(self):

        user = get_user()  # get user details from token
        portfolio_details = PortfolioQuery.get(user.id)[0]
        # stock_details = all_stocks_balance(user.id)
        
        # print(stock_details)
        
        create_csv(user, portfolio_details)
        
        # requests.get("http://127.0.0.1:5000/api/v1/exportfolio")
        
        # print(stock_details)
        
        return (
            {
                "message": "Portfolio downloaded",
            },
            200,
        )