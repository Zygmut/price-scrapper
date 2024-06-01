provider "grafana" {
  url  = "http://localhost:3000"
  auth = "remember to change this :)"
}

module "InfluxDB" {
  source = "./influxdb"
}
