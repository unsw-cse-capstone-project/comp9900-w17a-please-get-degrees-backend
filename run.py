import os
import sys
import subprocess

RUN_COMMAND = "flask run"

if __name__=='__main__':
    os.environ["FLASK_APP"] = "simvestr"
    os.environ["FLASK_ENV"] = "development"
    if sys.platform == "darwin":
        os.system(RUN_COMMAND)
    else:
        subprocess.run(RUN_COMMAND)