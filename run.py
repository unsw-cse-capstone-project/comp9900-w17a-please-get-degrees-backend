import os
import sys
import subprocess
import threading
import signal
from pathlib import Path

from simvestr.helpers.simulation import update_portfolio
from simvestr.helpers.setup_db import setup_new_db

RUN_COMMAND = "flask run"

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def service_shutdown(signum, frame):
    print('Caught signal %d \nExiting simultation! :)' % signum)
    raise ServiceExit

if __name__ == '__main__':
    os.environ["FLASK_APP"] = "simvestr"
    os.environ["FLASK_ENV"] = "development"
    
    # Setup a fresh database if it doesn't exist
    curr_dir = Path.cwd()
    db_path = curr_dir / "instance" / "simvestr.db"
    if not db_path.is_file():
        print('Aah new installation!')
        setup_new_db()
    else:
        print('Database file found, won\'t reset the db!')
        
        
    # Ask the user if they want to run the app in simulation mode
    # sim_mode = (input("Run the app in a simulation mode? : ")).lower()
    
    # Setting the sim_mode to ON for now (delete later after approval)
    sim_mode = 'y'
    
    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    # Call the subprocess for updating portfolio     
    try:
        if sim_mode in ["y", "yes", "yeah", "t", "true", "1", "on"]:
            print('Entering simulation mode :)')
            monitoring_thread = threading.Thread(target = update_portfolio)
            ''' Set daemon to False if you want to keep the simulation 
                running even after the flask app is terminated
            ''' 
            monitoring_thread.daemon = True
            monitoring_thread.start()

    except ServiceExit:
        print('Exiting simulation')
            
        
    # Run the app based on system specification        
    if sys.platform == "darwin" or sys.platform.lower() == "linux":
        os.system(RUN_COMMAND)
    else:
        subprocess.run(RUN_COMMAND)
