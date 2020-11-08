import os
import sys
import argparse
import subprocess
import threading
import signal
from pathlib import Path

from datetime import timedelta

from simvestr import create_app
from simvestr.helpers.simulation import update_portfolio
from simvestr.helpers.setup_db import setup_new_db
from simvestr.helpers.db import db

RUN_COMMAND = "flask run"

RUN_SETUP = True

SIM_DURATION = timedelta(minutes=1)
INTERVAL = timedelta(seconds=1)


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(signum, frame):
    print("Caught signal %d \nExiting simultation! :)" % signum)
    raise ServiceExit


# parser = argparse.ArgumentParser(
#     description="Run tool for Simvestr app",
# )
#
# parser.add_argument(
#     "-s",
#     "--simulation",
#     type=str,
#     default="n",
#     help="Toggle simulation mode"
# )
# subparsers = parser.add_subparsers(help="sub-parser help")
# sim_parser = subparsers.add_parser(
#     "simulation",
#     parents=[parser],
#     description="Simulation parser",
#     help="Manages simulation options"
# )
# sim_parser.add_argument(
#     "-d",
#     "--days",
#     help="Duration of the simulation in days"
# )
# sim_parser.add_argument(
#     "-h",
#     "--hours",
#     help="Duration of the simulation in hours"
# )
# sim_parser.add_argument(
#     "-m",
#     "--m",
#     help="Duration of the simulation in minutes"
# )
# sim_parser.add_argument(
#     "-s",
#     "--s",
#     help="Duration of the simulation in seconds"
# )
# sim_parser.add_argument(
#     "-i",
#     "--interval",
#     help="interval of the "
# )


if __name__ == "__main__":
    os.environ["FLASK_APP"] = "simvestr"
    os.environ["FLASK_ENV"] = "development"

    # Setup a fresh database if it doesn"t exist
    curr_dir = Path.cwd()
    db_path = curr_dir / "instance" / "simvestr.db"
    if not db_path.is_file() or RUN_SETUP:
        print("Aah new installation!")
        setup_new_db()
    else:
        print("Database file found, won\"t reset the db!")

    # Ask the user if they want to run the app in simulation mode
    # sim_mode = (input("Run the app in a simulation mode? : ")).lower()

    # Setting the sim_mode to ON for now (delete later after approval)
    sim_mode = "y"

    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    # Call the subprocess for updating portfolio     
    if sim_mode in ["y", "yes", "yeah", "t", "true", "1", "on"]:
        print("Entering simulation mode :)")
        sim_config = dict(
            duration=SIM_DURATION,
            interval=INTERVAL,
        )

        app = create_app(sim_config=sim_config)
        db.init_app(app)

        monitoring_thread = threading.Thread(
            target=update_portfolio,
            kwargs=dict(
                duration=SIM_DURATION,
                interval=INTERVAL,
                app=app,
            )
        )

    # Run the app based on system specification        
    if sys.platform == "darwin" or sys.platform.lower() == "linux":
        os.system(RUN_COMMAND)
    else:
        subprocess.run(RUN_COMMAND)
