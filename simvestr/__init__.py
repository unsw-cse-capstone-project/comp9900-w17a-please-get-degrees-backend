import datetime
from pathlib import Path
import threading

from flask import Flask
from flask_cors import CORS
import yaml

from simvestr.helpers.db import setup_new_db
from simvestr.helpers.simulation import update_portfolio
from simvestr.models import db

from simvestr.apis import blueprint as api

config_yml_path = Path(__file__).parent / "config.yml"


def load_yaml_config():
    with open(config_yml_path) as conf:
        config_data = yaml.safe_load(conf)
    return config_data


def get_delay(start_hour=21, start_minute=30):
    utc_today = datetime.datetime.now(datetime.timezone.utc)
    year, month, day = utc_today.year, utc_today.month, utc_today.day

    start_time = datetime.datetime(year, month, day, start_hour, start_minute, 0, 0, tzinfo=datetime.timezone.utc)

    delay = start_time - utc_today

    if delay.total_seconds() < 0:
        delay += datetime.timedelta(days=1)

    return delay.total_seconds()


def boot_app(app, run_setup):

    db_path = Path(app.instance_path) / "simvestr.db"
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=db_path,
        SQLALCHEMY_DATABASE_URI="sqlite:///" + str(db_path),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)

    if not db_path.is_file() :
        print("Aah new installation!")
        curr_dir = Path(__file__).parent.parent
        input_data = curr_dir / "resources" / "test_data_user.xlsx"
        setup_new_db(app, input_data)
    else:
        print("Database file found, won\"t reset the db!")


def create_app(test_config=None, sim_config=None, run_setup=False):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)

    config_yml = load_yaml_config()
    app.config["FINNHUB_API_KEY"] = config_yml["FINNHUB_API_KEY"]
    app.config["START_BALANCE"] = config_yml["START_BALANCE"]
    app.config["SLIPPAGE"] = config_yml["SLIPPAGE"]
    app.config["VALID_CHARS"] = config_yml["VALID_CHARS"]

    is_test = (test_config is not None)
    is_sim = (sim_config is None)
    is_test_and_sim = is_sim and is_test
    is_production = not is_test_and_sim
    # ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(exist_ok=True)
    except OSError:
        pass

    if is_production:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        boot_app(app, run_setup)
    elif is_test_and_sim:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    elif is_test:
        app.config.from_mapping(test_config)
    else:
        boot_app(app, run_setup)

    app.register_blueprint(api)

    CORS(app, supports_credentials=True)



    # Example how to add a simple route that renders a page
    @app.route("/")
    def index():
        return "Simvestr App"

    update_config = dict(
        duration=datetime.timedelta(weeks=10000),
        interval=datetime.timedelta(days=1),
    )
    delay = get_delay()
    daily_update_thread = threading.Timer(
        interval=delay,
        function=update_portfolio,
        kwargs=update_config,
    )
    daily_update_thread.daemon = True
    daily_update_thread.start()

    return app
