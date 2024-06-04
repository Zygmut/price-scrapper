# This variable is set via environment variable
# Why? Because I'm to lazy to be exporting each time or to
# pass the content of the variable each time I reload the docker daemon
# Also, given that the token _might_ change and that I get it dynamically
# I want to use it
variable "influx_token" {
  type      = string
  sensitive = true
}
