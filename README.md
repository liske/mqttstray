# mqttstray

*MQTT System Tray Icon*

![description](res/mqttstray.svg)


## About

This project provides a small python script which builds system tray icons from messages on MQTT subscribtions. The icons are build combining SVG template files and the jinja2 template processor to render images depending on the MQTT message payload. The payload needs to be JSON encoded.


## Usage

- create a python virtual env
- install missing dependencies within the env
- create a configuration


## Configuration


### MQTT

The main configuration file is `${XDG_CONFIG_HOME}/mqttstray/config`. It requires to contain a section for the MQTT connection:

```
[_MQTT]
host=127.0.0.1
port=8883
tls=True
verify=False
username=joe
password=foobar
```

The following settings are supported for the MQTT [constructor](https://pypi.org/project/paho-mqtt/#constructor-reinitialise) and MQTT [connect](https://pypi.org/project/paho-mqtt/#connect-reconnect-disconnect) invocation:
- `host` - the host used for the MQTT connection
- `port` - the port used for the MQTT connection (default: `1883`)
- `client_id` -
- `clean_session` -
- `transport` -
- `username` - MQTT authentication username (default: *None*)
- `password` - MQTT authentication password (default: *None*)

The following settings are supported for the MQTT [tls_set](https://pypi.org/project/paho-mqtt/#tls-set) invocation:
- `tls` - enable TLS for the MQTT connection (default: `False`)
- `verify` - verify the MQTT broker's X.509 certificate (default: `True`)
- `ca_certs` -
- `certfile` -
- `keyfile` -
- `ciphers` -
- `insecure` - ignore MQTT broker's X.509 certificate subject hostname (default: `False`)


### Icons

Any other section not beginning with a underscore (`_`) is handled as an icon configuration:

```
[xDrip mmol/l]
topic=android/broadcast/my-phone/xdrip
filename=xDrip/icon-mmol.svg
outdated=600
```


## Limitations

- no support for wildcard topics(, yet)
- currently only one topic per icon is supported
