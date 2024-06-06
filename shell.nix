# We pin to a specific nixpkgs commit for reproducibility.
{ pkgs? import (fetchTarball "https://github.com/Moraxyc/nixpkgs/tarball/add-logging-loki") {} }:


pkgs.mkShellNoCC {
  packages = with pkgs; [
    docker-compose
    jq
    pre-commit
    opentofu
    (python3.withPackages (ps: with ps; [
      requests
      beautifulsoup4
      click
      pandas
      influxdb-client
      python-logging-loki
    ]))
  ];

  shellHook = ''
    docker-compose up -d

    pre-commit install
    tofu -chdir=terraform init

    sleep 1

    export INFLUX_TOKEN=$(docker exec -t "influxdb" influx auth list --user admin --json | jq -r ".[0].token")
    export TF_VAR_influx_token=$(echo $INFLUX_TOKEN)
  '';
}
