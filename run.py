import os
import subprocess

if __name__=='__main__':
    os.environ['FLASK_APP'] = 'simvestr'
    os.environ['FLASK_ENV'] = "development"
    subprocess.run('flask run')