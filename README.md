# Electricity price scrapper

A simple-code probably-overengineered-environment python aplication to scrape electricity prices and deliver them into an [influxdb](https://www.influxdata.com/) to be later queried from [grafana](https://grafana.com/).

## ❄️ Environment

This project uses [`shell.nix`](./shell.nix) to manage the environment, so make sure to install the [nix package manager](https://nixos.org/download/).

After that, run `nix-shell` and it will _try_ execute [docker-compose](./docker-compose.yml) and automatically set `INFLUX_TOKEN` to a valid admin token from `influxdb` container.

>[!IMPORTANT]
> Remember to run `docker-daemon` if not `docker-compose` **will** fail

## 🧠 What I learnt

- **Nix**: `shell.nix` is probably going to be an standard for me from now on.
- **Grafana integration with Terraform**: Didn't know you could manage dashboards with Terraform. Though I've seen a problem when applying as `No data` is shown but when you re-run the query it magically works.
- **Loki**: I dipped my feet on managing logs with Loki. I _tried_ to work with Promtail but was to lazy to actually run it as this is a simple project and I won't be needing a log ingestor. _For now_, that is.
- **Pre-commit**: It's a useful tool to not commit trash to the repo, though I don't particularly enjoy setting it each time. That's where `shell.nix` comes in.
- **Doing custom Python decorators**: Nice way to not re-write stuff. I've used it at work multiple times at the time of writing this. I'd enjoyed more if it could be cleanly transformed into a context manager, but given that I need to cache _something_ the given solution weren't of my liking.
- **Actually finishing something**: Even though there are more stuff to do (clean up Terraform files, add Loki data source, structure the project better, write useful comments, etc) I'll just let it be a mark in history as a bad, over-engineered script that just scrapes some webpage for numbers and adds them to a database.
