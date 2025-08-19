from datetime import datetime

import pandas as pd


def format_hourly_data(dt: datetime) -> str:
    year = dt.strftime("%Y")
    date = dt.strftime("%Y%m%d")
    date_hour = dt.strftime("%Y%m%d%H")
    return (
        "https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow"
        f"/{year}/{date}/HourlyAQObs_{date_hour}.dat"
    )


def download_hourly_data(dt: datetime) -> pd.DataFrame:
    return pd.read_csv(
        format_hourly_data(dt),
        dialect="unix",
    )
