import os
import subprocess
import sys

RUN_COMMAND = "python setup.py sdist bdist_wheel"

if __name__=='__main__':
    if sys.platform == "darwin":
        os.system(RUN_COMMAND)
    elif sys.platform == "posix":
        os.system(RUN_COMMAND)
    else:
        subprocess.run(RUN_COMMAND)
