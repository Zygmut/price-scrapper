from requests import get  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
from influxdb_client import InfluxDBClient, Point  # type: ignore
from influxdb_client.client.write_api import SYNCHRONOUS  # type: ignore
from datetime import datetime, timezone, timedelta

from loki_logger import get_logger
from decorator import cache_to_file

import pandas as pd  # type: ignore
import os
import os.path
import click

LOGGER = get_logger("price_scrapper")


def to_utc(timestamp_str):
    local_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    local_timezone = timezone(timedelta(hours=+2))  # Spain timedelta
    local_time = local_time.replace(tzinfo=local_timezone)
    utc_time = local_time.astimezone(timezone.utc)
    return utc_time.strftime("%Y-%m-%d %H:%M:%S")


@cache_to_file("./cache/[year]/[month]/[day].html")
def read_contents(*, year: str, month: str, day: str) -> str:
    return get(
        f"https://infoenergia.es/luz/precio-luz-hoy?dia={year}-{month}-{day}"
    ).text


def parse_cell(cell: Tag) -> dict[str, str | float]:
    cells: list[str] = [element.text for element in cell.contents]

    timestamp = f"{cells[1][:-1]}:00:00"
    price = cells[-2].split(" ")[0].replace(",", ".")

    return {
        "timestamp": timestamp,
        "euro_per_kWh": float(price),
    }


@click.command()
@click.option(
    "--token",
    default=os.getenv("INFLUX_TOKEN"),
    help="Influx token",
)
@click.option(
    "--url",
    default="http://localhost:8086",
    help="Influx url",
)
@click.option(
    "--org",
    default="cool_org",
    help="Influx organization name",
)
@click.option(
    "--year",
    default=datetime.today().strftime("%Y"),
    help="The year to fetch the prices",
)
@click.option(
    "--month",
    default=datetime.today().strftime("%m"),
    help="The month to fetch the prices fmt",
)
@click.option(
    "--day",
    default=datetime.today().strftime("%d"),
    help="The day to fetch the prices fmt",
)
def main(token: str, url: str, org: str, year: str, month: str, day: str) -> None:

    date = "-".join([year, month, day])

    soup = BeautifulSoup(read_contents(year=year, month=month, day=day), "html.parser")

    cells = soup.find_all("div", {"class": "th"})

    parsed_data = map(parse_cell, cells)

    df = pd.DataFrame(parsed_data)

    df["timestamp"] = (date + " " + df["timestamp"]).apply(to_utc)
    df.set_index("timestamp", inplace=True)

    df.to_csv(os.path.join(".", "out", f"{date}.csv"))

    write_client = InfluxDBClient(
        token=token,
        url=url,
        org=org,
    )

    write_api = write_client.write_api(write_options=SYNCHRONOUS)

    points = [
        Point("euro_per_kWh").field("price", float(float(price.iloc[0]))).time(time)
        for time, price in df.iterrows()
    ]

    LOGGER.info(f"Adding {len(points)} to influxDB")
    write_api.write(
        bucket="electricity_price", org=os.getenv("INFLUX_ORG"), record=points
    )


if __name__ == "__main__":
    main()
