# We pin to a specific nixpkgs commit for reproducibility.
{ pkgs? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-23.11") {} }:

pkgs.mkShellNoCC {
  packages = with pkgs; [
    docker-compose
    (python3.withPackages (ps: with ps; [
      requests
      beautifulsoup4
      click
      pandas
      python-dotenv
      influxdb-client
    ]))
  ];

  # *** Environment Variables ***
  INFLUX_TOKEN="i-like-bananas-as-much-as-radiation";
  INFLUX_HOST="http://localhost:8086";
  INFLUX_ORG="cool_org";
}
