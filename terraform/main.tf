module "InfluxDB" {
  source = "./influx"

  token = var.influx_token
}
