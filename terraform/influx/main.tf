resource "grafana_folder" "this" {
  title = "InfluxDB"
}

resource "grafana_dashboard" "this" {
  for_each = fileset("${path.module}/dashboard", "*.json")

  config_json = file("${path.module}/dashboard/${each.key}")
  folder      = grafana_folder.this.id
}
