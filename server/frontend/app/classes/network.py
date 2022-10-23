#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import subprocess as sp
import urllib.request
import requests as rq
import random
import re
import sys
import time
import netifaces as ni
import base64
import random
import requests

from wifi import Cell
from os import path, remove
from io import BytesIO
from app.utils import terminate_process, read_config


class Network(object):

    # A dictionary to map all ports to socket objects.
    socket_objs = {}

    def __init__(self):
        self.proxy_ip = False
        self.proxy_port = False
        self.iface_out = read_config(("network", "out"))
        self.enable_interface(self.iface_out)
        self.random_choice_alphabet = "abcdef1234567890"

    def check_status(self):
        """
            The method check_status check the IP addressing of each interface 
            and return their associated IP.

            :return: dict containing each interface status.
        """

        ctx = {"interfaces": {
            self.iface_out: False,
            "eth0": False},
            "internet": self.check_internet()}

        for iface in ctx["interfaces"].keys():
            try:
                ip = ni.ifaddresses(iface)[ni.AF_INET][0]["addr"]
                if not ip.startswith("127") or not ip.startswith("169.254"):
                    ctx["interfaces"][iface] = ip
            except:
                ctx["interfaces"][iface] = "Interface not connected or present."
        return ctx

    def wifi_list_networks(self):
        """
            The method wifi_list_networks list the available WiFi networks
            by using wifi python package.
            :return: dict - containing the list of Wi-Fi networks.
        """
        networks = []
        try:
            for n in Cell.all(self.iface_out):
                if n.ssid not in [n["ssid"] for n in networks] and n.ssid and n.encrypted:
                    networks.append(
                        {"ssid": n.ssid, "type": n.encryption_type})
            return {"networks": networks}
        except:
            return {"networks": []}

    @staticmethod
    def wifi_setup(ssid, password):
        """
            Edit the wpa_supplicant file with provided credentials.
            If the ssid already exists, just update the password. Otherwise
            create a new entry in the file.

            :return: dict containing the status of the operation
        """
        if len(password) >= 8 and len(ssid):
            found = False
            networks = []
            header, content = "", ""

            with open("/etc/wpa_supplicant/wpa_supplicant.conf") as f:
                content = f.read()
                blocks = content.split("network={")
                header = blocks[0]

                for block in blocks[1:]:
                    net = {}
                    for line in block.splitlines():
                        if line and line != "}":
                            if "priority=10" not in line.strip():
                                key, val = line.strip().split("=")
                            if key != "disabled":
                                net[key] = val.replace("\"", "")
                    networks.append(net)

                for net in networks:
                    if net["ssid"] == ssid:
                        net["psk"] = password.replace('"', '\\"')
                        net["priority"] = "10"
                        found = True

                if not found:
                    networks.append({
                        "ssid": ssid,
                        "psk": password.replace('"', '\\"'),
                        "key_mgmt": "WPA-PSK",
                        "priority": "10"
                    })

            with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w+") as f:
                content = header
                for network in networks:
                    net = "network={\n"
                    for k, v in network.items():
                        if k in ["ssid", "psk"]:
                            net += "    {}=\"{}\"\n".format(k, v)
                        else:
                            net += "    {}={}\n".format(k, v)
                    net += "}\n\n"
                    content += net
                if f.write(content):
                    return {"status": True,
                            "message": "Configuration saved"}
                else:
                    return {"status": False,
                            "message": "Error while writing wpa_supplicant configuration file."}
        else:
            return {"status": False,
                    "message": "Empty SSID or/and password length less than 8 chars."}

    def wifi_connect(self):
        """
            Connect to one of the WiFi networks present in the wpa_supplicant.conf.
            :return: dict containing the TinyCheck <-> AP status.
        """

        # Kill wpa_supplicant instances, if any.
        terminate_process("wpa_supplicant")
        # Launch a new instance of wpa_supplicant.
        sp.Popen(["wpa_supplicant", "-B", "-i", self.iface_out, "-c",
                  "/etc/wpa_supplicant/wpa_supplicant.conf"]).wait()
        # Check internet status
        for _ in range(1, 40):
            if self.check_internet():
                return {"status": True,
                        "message": "Wifi connected"}
            time.sleep(1)

        return {"status": False,
                "message": "Wifi not connected"}




    

    ##### HANDLE ALL OF THE PROXY STUFF

    # Starts a proxy service, returning info for the new proxy.
    def start_proxy(self):
        """
            The start_proxy method generates a proxy access and provides
            the ip address and port to the GUI.

            :return: dict containing the status of the proxy
        """

        # Re-ask to enable interface, sometimes it just go away.
        if not self.enable_interface(self.iface_out):
            return {"status": False,
                    "message": "Interface not present."}


        # Stop any existing socket
        if self.proxy_port:
            self.stop_proxy()


        ### Calculate parameters

        # Use a pre-specified IP address, if specified. Otherwise, use the external IP.
        self.proxy_ip = read_config(("network", "override_ip"))
        if self.proxy_ip == "":
            self.proxy_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')

        # Identify an unused port within a preset range.
        port_is_valid = False
        bounds_low = read_config(("network", "port_bounds_low"))
        bounds_high = read_config(("network", "port_bounds_high"))

        # Keep looping until a valid port is identified.
        # This will also result in a socket being generated.
        while not port_is_valid:
            # Generate a random port number.
            self.proxy_port = random.randrange(bounds_low, bounds_high + 1);
            port_is_valid = True
            print(self.proxy_port)

            if self.proxy_port < 0:
                port_is_valid = False
            elif self.proxy_port > 65535:
                port_is_valid = False
            else:
                # Attempt to allocate the socket.
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind(("0.0.0.0", self.proxy_port))

                    # Store the socket object for future use.
                    Network.socket_objs[self.proxy_port] = sock
                # The most likely case for an exception is that the port is already binded.
                except Exception as e:
                    port_is_valid = False
        

        # Launch hostapd
        return {"status": True,
                "message": "Proxy started",
                "proxy_ip": self.proxy_ip,
                "proxy_port": self.proxy_port}

    # Stops a proxy by closing the socket and removing the entry.
    def stop_proxy(self):
        Network.socket_objs[self.proxy_port].close()

        Network.socket_objs.pop(self.proxy_port)

    def enable_interface(self, iface):
        """
            This enable interfaces, with a simple check. 
            :return: bool if everything goes well 
        """
        # sh = sp.Popen(["ip" ,"a","s", iface],
        #               stdout=sp.PIPE, stderr=sp.PIPE)
        # sh = sh.communicate()
        # if b",UP" in sh[0]:
        #     return True  # The interface is up.
        # elif sh[1]:
        #     return False  # The interface doesn't exists (most of the cases).
        # else:
        #     sp.Popen(["ip","link","set", iface, "up"]).wait()
        #     return True
        return True

    def check_internet(self):
        """
            Check the internet link just with a small http request
            to an URL present in the configuration

            :return: bool - if the request succeed or not.
        """
        try:
            url = read_config(("network", "internet_check"))
            requests.get(url, timeout=10)
            return True
        except:
            return False
