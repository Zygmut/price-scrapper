from requests import get  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
from influxdb_client import InfluxDBClient, Point  # type: ignore
from influxdb_client.client.write_api import SYNCHRONOUS  # type: ignore
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

import pandas as pd  # type: ignore
import os
import os.path
import click


def to_utc(timestamp_str):
    local_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    local_timezone = timezone(timedelta(hours=+2))  # Spain timedelta
    local_time = local_time.replace(tzinfo=local_timezone)
    utc_time = local_time.astimezone(timezone.utc)
    return utc_time.strftime("%Y-%m-%d %H:%M:%S")


def read_contents(date: str) -> str:
    FILE_PATH = os.path.join(".", "cache", f"{date}.html")

    if os.path.exists(FILE_PATH):
        print(f"Reading {date}.html from the cache")
        with open(FILE_PATH, "r") as file:
            content = file.read()

        return content

    page_content: str = get(
        f"https://infoenergia.es/luz/precio-luz-hoy?dia={date}"
    ).text

    with open(FILE_PATH, "w") as file:
        file.write(page_content)

    return page_content


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
    "--date",
    default=datetime.today().strftime("%Y-%m-%d"),
    help="The date to fetch the prices",
)
def main(date: str) -> None:
    load_dotenv()

    soup = BeautifulSoup(read_contents(date), "html.parser")

    cells = soup.find_all("div", {"class": "th"})

    parsed_data = map(parse_cell, cells)

    df = pd.DataFrame(parsed_data)

    df["timestamp"] = (date + " " + df["timestamp"]).apply(to_utc)
    df.set_index("timestamp", inplace=True)

    df.to_csv(os.path.join(".", "out", f"{date}.csv"))

    assert os.getenv("INFLUX_HOST")
    assert os.getenv("INFLUX_TOKEN")
    assert os.getenv("INFLUX_ORG")

    write_client = InfluxDBClient(
        url=os.getenv("INFLUX_HOST"),
        token=os.getenv("INFLUX_TOKEN"),
        org=os.getenv("INFLUX_ORG"),
    )

    write_api = write_client.write_api(write_options=SYNCHRONOUS)

    points = [
        Point("euro_per_kWh").field("price", float(float(price.iloc[0]))).time(time)
        for time, price in df.iterrows()
    ]

    write_api.write(
        bucket="electricity_price", org=os.getenv("INFLUX_ORG"), record=points
    )


if __name__ == "__main__":
    main()
