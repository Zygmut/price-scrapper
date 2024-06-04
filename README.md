# Electricity price scrapper

A simple-code probably-overengineered-environment python aplication to scrape electricity prices and deliver them into an [influxdb](https://www.influxdata.com/) to be later queried from [grafana](https://grafana.com/).

## ❄️ Environment

This project uses [`shell.nix`](./shell.nix) to manage the environment, so make sure to install the [nix package manager](https://nixos.org/download/).

After that, run `nix-shell` and it will _try_ execute [docker-compose](./docker-compose.yml) and automatically set `INFLUX_TOKEN` to a valid admin token from `influxdb` container.

>[!IMPORTANT]
> Remember to run `docker-daemon` if not `docker-compose` **will** fail
