#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import jsonify, Blueprint
from app.classes.device import Device

device_bp = Blueprint("device", __name__)


@device_bp.route("/get/<token>/<port>", methods=["GET"])
def api_device_get(token, port):
    """ Get device assets """
    return jsonify(Device(token, port).get())
