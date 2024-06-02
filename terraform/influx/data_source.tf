resource "grafana_data_source" "this" {
  type                = "influxdb"
  name                = "InfluxDB-SQL"
  url                 = "localhost:8086"
  basic_auth_enabled  = true
  basic_auth_username = "username"

  json_data_encoded = jsonencode({
    httpMethod        = "POST"
    prometheusType    = "Mimir"
    prometheusVersion = "2.4.0"
  })

  secure_json_data_encoded = jsonencode({
    basicAuthPassword = "password"
  })
}
