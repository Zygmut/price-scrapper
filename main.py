from requests import get  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

import pandas as pd  # type: ignore
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

    # export it to Prometheus
    registry = CollectorRegistry()
    euro_per_kWh_gauge = Gauge(
        "energy_price_euro_per_kWh",
        "Energy Price in Euro per kWh",
        ["timestamp"],
        registry=registry,
    )

    for time, price in df.iterrows():
        timestamp = int(datetime.strptime(time, "%Y-%m-%d %H:%M:%S").timestamp())
        euro_per_kWh_gauge.labels(timestamp=timestamp).set(float(price.iloc[0]))

    # Push metrics to Prometheus
    push_to_gateway(
        "http://host.docker.internal:9091",
        job="energy_price_scraper",
        registry=registry,
    )


if __name__ == "__main__":
    main()
