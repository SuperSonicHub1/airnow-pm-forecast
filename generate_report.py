from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

from airnow_pm_forecast.dat_download import download_hourly_data

CAMBRIDGE_STATIONS = [
    "250250002",
    "840250250045",
    "840250251004",
    "250250042",
    "250250044",
]


def current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


def past_n_hours(dt: datetime, n: int) -> list[datetime]:
    floored_datetime = dt.replace(minute=0, second=0, microsecond=0)
    return [floored_datetime - i * timedelta(hours=1) for i in range(1, n + 1)][::-1]


def process(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    df = df[["AQSID", "SiteName", "ValidDate", "ValidTime", "PM25"]]
    # Select for stations of interest
    df = df[df["AQSID"].isin(CAMBRIDGE_STATIONS)]
    # Parse date
    df = df.assign(
        date=pd.to_datetime(
            df["ValidDate"] + " " + df["ValidTime"],
            utc=True,
            format="%m/%d/%Y %H:%M",
        )
    )[["SiteName", "PM25", "date"]].sort_values("date")
    df_avg = df[["date", "PM25"]].groupby("date").mean()
    df_by_location = df.pivot(index="date", columns="SiteName", values="PM25")
    return df_by_location, df_avg


def create_plot():
    ct = current_utc_time()
    past_rows = pd.concat(
        [download_hourly_data(dt) for dt in past_n_hours(ct - timedelta(hours=1), 24)]
    )

    df_by_location, df_avg = process(past_rows)
    # Continue: https://pandas.pydata.org/docs/getting_started/intro_tutorials/09_timeseries.html

    fig, (ax_avg, ax_location) = plt.subplots(
        2, 1, sharex=True, sharey=True, figsize=(8.5, 11)
    )

    XLABEL = "Measurement time (UTC)"
    YLABEL = "Concentration of PM₂.₅ (μg/m^3)"

    formatted_date = ct.strftime("%B %d, %Y")
    df_avg.plot.line(
        title=f"Average PM₂.₅ concentration as of {formatted_date}",
        xlabel=XLABEL,
        ylabel=YLABEL,
        legend=False,
        ax=ax_avg,
    )

    df_by_location.plot.line(
        title=f"PM₂.₅ concentration by station as of {formatted_date}",
        xlabel=XLABEL,
        ylabel=YLABEL,
        ax=ax_location,
    )

    ax_location.legend().set_title("Site name")

    return fig


resources = Path.cwd() / "resources"
resources.mkdir(exist_ok=True)
fig = create_plot()
fig.savefig(str(resources / "report.png"))
fig.savefig(str(resources / "report.pdf"))
