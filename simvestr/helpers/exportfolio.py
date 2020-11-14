# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 11:57:41 2020
@author: Kovid
"""

import xlsxwriter

def create_csv(file_path, file_basename, user, portfolio_details, portfolio_value_user):
    workbook = xlsxwriter.Workbook(f"{file_path}/{file_basename}")
    worksheet = workbook.add_worksheet()

    heading_format_1 = workbook.add_format(
        {"bold": True, "bg_color": "#28B463", "font_color": "black"}
    )
    cell_format_1 = workbook.add_format({"bg_color": "#D2B4DE", "font_color": "black"})

    heading_format_2 = workbook.add_format(
        {"bold": True, "bg_color": "#2980B9", "font_color": "black"}
    )
    cell_format_2 = workbook.add_format({"bg_color": "#F7DC6F", "font_color": "black"})

    worksheet.write("A1", "Name", heading_format_1)
    worksheet.write("B1", f"{user.first_name} {user.last_name}", cell_format_1)

    worksheet.write("A2", "Date Joined", heading_format_2)
    worksheet.write("B2", f"{user.date_joined.date()}", cell_format_2)

    worksheet.write("A3", "Balance", heading_format_1)
    worksheet.write("B3", f'{portfolio_details["balance"]}', cell_format_1)

    worksheet.write("A4", "Total Value", heading_format_2)
    worksheet.write("B4", f'{portfolio_details["total_value"]}', cell_format_2)

    worksheet.write("A5", "Cash Balance", heading_format_1)
    worksheet.write(
        "B5",
        f'{portfolio_details["total_value"] + portfolio_details["balance"]}',
        cell_format_1,
    )

    # Add a format. Light red fill with dark red text.
    format1 = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})

    # Add a format. Green fill with dark green text.
    format2 = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})

    stock_heading_format = workbook.add_format(
        {"bold": True, "bg_color": "#5DADE2", "font_color": "black"}
    )

    row = 7
    worksheet.write(f"C{row}", "Stocks", stock_heading_format)
    worksheet.write(f"D{row}", "Symbol", stock_heading_format)
    worksheet.write(f"E{row}", "Quantity", stock_heading_format)
    worksheet.write(f"F{row}", "Quote", stock_heading_format)
    worksheet.write(f"G{row}", "Value", stock_heading_format)
    worksheet.write(f"H{row}", "Weighted Avg Fee", stock_heading_format)
    worksheet.write(f"I{row}", "Weighted Average", stock_heading_format)
    worksheet.write(f"J{row}", "Return", stock_heading_format)

    for stock_dict in portfolio_value_user:
        row += 1
        stock = Stock.query.filter_by(symbol=stock_dict["symbol"]).first()
        worksheet.write(f"C{row}", f"{stock.name}")
        worksheet.write(f"D{row}", f'{stock_dict["symbol"]}')
        worksheet.write(f"E{row}", f'{stock_dict["quantity"]}')
        if stock_dict["current"] < stock_dict["buy"]["weighted_average"]:
            worksheet.write(f"F{row}", f'{stock_dict["current"]}', format1)
            worksheet.write(
                f"I{row}", f'{stock_dict["buy"]["weighted_average"]}', format2
            )
        else:
            worksheet.write(f"F{row}", f'{stock_dict["current"]}', format2)
            worksheet.write(
                f"I{row}", f'{stock_dict["buy"]["weighted_average"]}', format1
            )
        worksheet.write(f"G{row}", f'{stock_dict["value"]}')
        worksheet.write(f"H{row}", f'{stock_dict["buy"]["weighted_average_fee"]}')
        worksheet.write(f"J{row}", f'{stock_dict["return"]}')

    workbook.close()
