import os
import threading
import signal
from datetime import timedelta

from simvestr import create_app
from simvestr.helpers.simulation import update_portfolio
from simvestr.helpers.db import db

RUN_COMMAND = "flask run"

RUN_SETUP = False

SIM_DURATION = timedelta(minutes=5)
INTERVAL = timedelta(seconds=3)


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(signum, frame):
    print("Caught signal %d \nExiting simultation! :)" % signum)
    raise ServiceExit


if __name__ == "__main__":
    os.environ["FLASK_APP"] = "simvestr"
    os.environ["FLASK_ENV"] = "development"


    # Setting the sim_mode to ON for now (delete later after approval)
    sim_mode = "n"

    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    # Call the subprocess for updating portfolio     
    if sim_mode in ["y", "yes", "yeah", "t", "true", "1", "on"]:
        print("Entering simulation mode :)")
        sim_config = dict(
            duration=SIM_DURATION,
            interval=INTERVAL,
            new_day=True,
        )

        app = create_app(sim_config=sim_config)
        db.init_app(app)
        sim_config["app"] = app
        monitoring_thread = threading.Thread(
            target=update_portfolio,
            kwargs=sim_config,
            daemon=True
        )
        monitoring_thread.start()

    app = create_app(run_setup=True)
    app.run(debug=True)
