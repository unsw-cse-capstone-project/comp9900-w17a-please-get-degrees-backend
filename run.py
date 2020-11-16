import os

from simvestr import create_app

if __name__ == "__main__":
    os.environ["FLASK_APP"] = "simvestr"
    os.environ["FLASK_ENV"] = "developement"

    app = create_app(run_setup=False)
    app.run(debug=True)
