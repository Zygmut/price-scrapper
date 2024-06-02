provider "grafana" {
  url  = "http://localhost:3000"
  auth = "admin:admin"
}

module "InfluxDB" {
  source = "./influxdb"
}
