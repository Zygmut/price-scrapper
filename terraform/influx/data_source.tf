resource "grafana_data_source" "this" {
  type = "influxdb"
  name = "InfluxDB-FLUX"
  url  = "http://influxdb:8086"

  is_default = true

  json_data_encoded = jsonencode({
    authType     = "default"
    organization = "cool_org"
    version      = "Flux"
    httpMode     = "POST"
  })

  secure_json_data_encoded = jsonencode({
    token = var.token
  })
}
