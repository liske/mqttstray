#!/usr/bin/env python
# -*- coding: utf-8 -*-


#
# mqttstray - MQTT System Tray Icon
#
# Authors:
#   Thomas Liske <thomas@fiasko-nw.net>
#
# Copyright Holder:
#   2018 (C) Thomas Liske [http://fiasko.io/]
#
# License:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this package; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#


# python built-in packages
import configparser
import getpass
import io
import json
import os
import socket
import ssl
import threading

# additional python packages
import cairosvg
import jinja2
import paho.mqtt.client as mqtt
from PIL import Image
import pystray
from xdg import XDG_CONFIG_HOME

# global stuff
APP_NAME = "mqttstray"
APP_ICON = Image.open(os.path.join(
  os.path.dirname(__file__),
  "res",
  "mqttstray.png"
))
CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, APP_NAME)
TMPL_ENV = jinja2.Environment(
  loader=jinja2.FileSystemLoader(searchpath=CONFIG_DIR)
)


class MQTT(threading.Thread):
  def __init__(self, config, section):
    threading.Thread.__init__(self)
    
    self.subs = {}
    self.mqttc = mqtt.Client(
      client_id=config[section].get("client_id", "{}@{}".format(getpass.getuser(), socket.getfqdn())),
      clean_session=False,
      transport=config[section].get("transport", "tcp")
    )
    self.mqttc.enable_logger()
    
    if config[section].getboolean("tls", False):
      creq = ssl.CERT_REQUIRED
      if not config[section].getboolean("verify", True):
        creq = ssl.CERT_NONE
    
      self.mqttc.tls_set(
        ca_certs=config[section].get("ca_certs"),
        certfile=config[section].get("certfile"),
        keyfile=config[section].get("keyfile"),
        cert_reqs=creq,
        ciphers=config[section].get("ciphers")
      )
      self.mqttc.tls_insecure_set(not config[section].getboolean("insecure", False))
    
    self.mqttc.on_message = self.on_message

    if config[section].get("username"):
      self.mqttc.username_pw_set(config[section].get("username"), config[section].get("password"))
  
    self.mqttc.connect(
      host=config[section].get("host"),
      port=config[section].getint("port", 1883)
    )
    self.start()

  def on_message(self, client, userdata, message):
    if message.topic in self.subs:
      data = json.loads(
        message.payload.decode("utf-8")
      )
      for icon in self.subs[message.topic]:
        icon.update(message.topic, data)
    else:
      print("Oops, no subscribers for topic '{}'?!".format(message.topic))

  def register(self, topic, icon):
    if topic not in self.subs:
      self.subs[topic] = []
      self.mqttc.subscribe(topic)

    self.subs[topic].append(icon)

  def run(self):
    self.mqttc.loop_forever()


class Icon(threading.Thread):
  def __init__(self, config, section, mqtt):
    threading.Thread.__init__(self)
    self.tmpl = TMPL_ENV.get_template(config.get(section, "filename"))
    self.icon = pystray.Icon(name=section, title=section)
    self.start()

    mqtt.register(config.get(section, "topic"), self)

  def update(self, topic, data):
    try:
      svg = self.tmpl.render(payload=data)
      output = cairosvg.svg2png(svg)
      self.icon.icon = Image.open(io.BytesIO(output))
    except:
      self.icon.icon = APP_ICON
      pass

  def run(self):
    self.icon.icon = APP_ICON
    self.icon.run()


def main():
  config = configparser.ConfigParser()
  config.read(os.path.join(CONFIG_DIR, "config"))

  mqtt = MQTT(config, "_MQTT")
  threads = [ mqtt ]
  for section in [x for x in config.sections() if not x.startswith("_")]:
    threads.append( Icon(config, section, mqtt) )

  for t in threads:
      t.join()


if __name__ == '__main__':
  main()
