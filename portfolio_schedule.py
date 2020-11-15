import datetime
import threading

from simvestr import create_app
from simvestr import update_portfolio
from simvestr.helpers.utils import get_delay, load_yaml_config

if __name__ == '__main__':
    config_yml = load_yaml_config()
    delay = get_delay()

    app = create_app()

    update_config = dict(
        duration=datetime.timedelta(**config_yml["UPDATE_DURATION"]),
        interval=datetime.timedelta(**config_yml["UPDATE_INTERVAL"]),
        app=app
    )

    daily_update_thread = threading.Timer(
        interval=delay,
        function=update_portfolio,
        kwargs=update_config,
    )

    daily_update_thread.start()
