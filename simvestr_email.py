# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 00:55:31 2020

@author: Kovid
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(user_email_address, message_text, message_content):
    
    from_address = 'simvestr@gmail.com'
    # to_address = 'z5240067@ad.unsw.edu.au'
    to_address = user_email_address
    
    message_content = 'Hello Investor,\n\n' + message_content + '\n\nSimvestr Pvt. Ltd.\nSyndey, Australia'
    
    message = MIMEMultipart('Simvestr')
    # message['Subject'] = 'User created successfully'
    message['Subject'] = message_text
    message['From'] = from_address
    message['To'] = to_address
    
    # message_content = 'Congratulations, you have been registered successfully. Happy investing!'
    content = MIMEText(message_content, 'plain')
    
    message.attach(content)
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(from_address, 'simvestr@123')
    mail.sendmail(from_address,to_address, message.as_string())
    mail.close()
    
# send_email('z5240067@ad.unsw.edu.au', 'User created successfully', 'Congratulations, you have been registered successfully. Happy investing!')