# We pin to a specific nixpkgs commit for reproducibility.
{ pkgs? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-23.11") {} }:

pkgs.mkShellNoCC {
  packages = with pkgs; [
    docker-compose
    jq
    (python3.withPackages (ps: with ps; [
      requests
      beautifulsoup4
      click
      pandas
      influxdb-client
    ]))
  ];

  shellHook = ''
    docker-compose up -d

    sleep 0.5

    export INFLUX_TOKEN=$(docker exec -t "influxdb" influx auth list --user admin --json | jq -r ".[0].token")
  '';
}
