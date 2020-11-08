from pathlib import Path


from flask import Flask
from flask_cors import CORS
import yaml


config_yml_path = Path(__file__).parent / "config.yml"



def load_yaml_config():
    with open(config_yml_path) as conf:
        config_data = yaml.safe_load(conf)
    return config_data


def create_app(test_config=None, sim_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=Path(app.instance_path) / "simvestr.sqlite",
        SQLALCHEMY_DATABASE_URI="sqlite:///"
        + str(Path(app.instance_path) / "simvestr.db"),
    )
    config_yml = load_yaml_config()
    app.config["FINNHUB_API_KEY"] = config_yml["Finnhub API Key"]
    app.config["START_BALANCE"] = config_yml["START_BALANCE"]

    from simvestr.models import db

    db.init_app(app)

    from simvestr.apis import blueprint as api

    app.register_blueprint(api)

    CORS(app, supports_credentials=True)

    is_test = (test_config is not None)
    is_sim = (sim_config is None)
    is_test_and_sim = is_sim and is_test
    is_production = not is_test_and_sim

    if is_production:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    elif is_test_and_sim:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    elif is_test:
        app.config.from_mapping(test_config)
    # ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(exist_ok=True)
    except OSError:
        pass

    # Example how to add a simple route that renders a page
    @app.route("/")
    def index():
        return "Simvestr App"



    return app
