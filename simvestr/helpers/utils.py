import datetime
from pathlib import Path

import yaml

config_yml_path = Path(__file__).parent.parent / "config.yml"

def get_delay(start_hour=21, start_minute=30):
    utc_today = datetime.datetime.now(datetime.timezone.utc)
    year, month, day = utc_today.year, utc_today.month, utc_today.day

    start_time = datetime.datetime(year, month, day, start_hour, start_minute, 0, 0, tzinfo=datetime.timezone.utc)

    delay = start_time - utc_today

    if delay.total_seconds() < 0:
        delay += datetime.timedelta(days=1)

    return delay.total_seconds()


def load_yaml_config():
    with open(config_yml_path) as conf:
        config_data = yaml.safe_load(conf)
    return config_data
