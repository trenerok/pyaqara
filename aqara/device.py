"""Aqara Devices"""

import logging

from aqara.const import (
    AQARA_DEVICE_HT,
    AQARA_DEVICE_MOTION,
    AQARA_DEVICE_MAGNET,
    AQARA_DEVICE_SWITCH,
    AQARA_SWITCH_ACTION_CLICK,
    AQARA_SWITCH_ACTION_DOUBLE_CLICK,
    AQARA_SWITCH_ACTION_LONG_CLICK_PRESS,
    AQARA_SWITCH_ACTION_LONG_CLICK_RELEASE
)

_LOGGER = logging.getLogger(__name__)

BUTTON_ACTION_MAP = {
    "click": AQARA_SWITCH_ACTION_CLICK,
    "double_click": AQARA_SWITCH_ACTION_DOUBLE_CLICK,
    "long_click_press": AQARA_SWITCH_ACTION_LONG_CLICK_PRESS,
    "long_click_release": AQARA_SWITCH_ACTION_LONG_CLICK_RELEASE
}

def create_device(gateway, model, sid):
    """Device factory"""
    if model == AQARA_DEVICE_HT:
        return AqaraHTSensor(gateway, sid)
    elif model == AQARA_DEVICE_MOTION:
        return AqaraMotionSensor(gateway, sid)
    elif model == AQARA_DEVICE_MAGNET:
        return AqaraContactSensor(gateway, sid)
    elif model == AQARA_DEVICE_SWITCH:
        return AqaraSwitchSensor(gateway, sid)
    else:
        raise RuntimeError('Unsupported device type: {} [{}]'.format(model, sid))

class AqaraBaseDevice(object):
    """AqaraBaseDevice"""
    def __init__(self, gateway, model, sid):
        self._gateway = gateway
        self._model = model
        self._sid = sid
        self._update_callback = None
        self._properties = {}

    @property
    def sid(self):
        """property: sid"""
        return self._sid

    @property
    def model(self):
        """property: model"""
        return self._model

    def set_update_callback(self, update_callback):
        """set update_callback"""
        self._update_callback = update_callback

    def update_now(self):
        """force read sensor data"""
        self._gateway.read_device(self._sid)

    def on_update(self, data):
        """handler for sensor data update"""
        self.do_update(data)
        if self._update_callback != None:
            self._update_callback()

    def on_heartbeat(self, data):
        """handler for heartbeat"""
        self.do_heartbeat(data)
        if self._update_callback != None:
            self._update_callback()

    def do_update(self, data):
        """update sensor state according to data"""
        pass

    def do_heartbeat(self, data):
        """update heartbeat"""
        pass

    def log_warning(self, msg):
        """log warning"""
        self._log(_LOGGER.warning, msg)

    def _log(self, log_func, msg):
        """log"""
        log_func('[%s] %s: %s', self._model, self._sid, msg)

class AqaraHTSensor(AqaraBaseDevice):
    """AqaraHTSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_HT, gateway, sid)
        self._properties = {
            "temperature": 0,
            "humidity": 0
        }

    @property
    def temperature(self):
        """property: temperature (unit: C)"""
        return self._properties["temperature"]

    @property
    def humidity(self):
        """property: humidity (unit: %)"""
        return self._properties["humidity"]

    def do_update(self, data):
        if "temperature" in data:
            self._properties["temperature"] = self.parse_value(data["temperature"])
        if "humidity" in data:
            self._properties["humidity"] = self.parse_value(data["humidity"])

    def do_heartbeat(self, data):
        # heartbeat for HT sensor contains the same data as report
        self.do_update(data)

    @staticmethod
    def parse_value(str_value):
        """parse sensor_ht values"""
        return round(int(str_value) / 100, 1)


class AqaraContactSensor(AqaraBaseDevice):
    """AqaraContactSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_MAGNET, gateway, sid)
        self._properties = {
            "triggered": False,
            "voltage": 0
        }

    @property
    def triggered(self):
        """property: triggered (bool)"""
        return self._properties["triggered"]

    def do_update(self, data):
        if "status" in data:
            self._properties["triggered"] = data["status"] == "open"

    def do_heartbeat(self, data):
        if "voltage" in data:
            self._properties["voltage"] = int(data["voltage"])

class AqaraMotionSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_MOTION, gateway, sid)
        self._properties = {
            "triggered": False,
            "voltage": 0
        }

    @property
    def triggered(self):
        """property: triggered (bool)"""
        return self._properties["triggered"]

    def do_update(self, data):
        if "status" in data:
            self._properties["triggered"] = data["status"] == "motion"
        else:
            self._properties["triggered"] = False

    def do_heartbeat(self, data):
        if "voltage" in data:
            self._properties["voltage"] = int(data["voltage"])

class AqaraSwitchSensor(AqaraBaseDevice):
    """AqaraMotionSensor"""
    def __init__(self, gateway, sid):
        super().__init__(AQARA_DEVICE_SWITCH, gateway, sid)
        self._properties = {
            "action": None,
            "voltage": 0
        }

    @property
    def action(self):
        """property: last_action"""
        return self._properties["action"]

    def do_update(self, data):
        if "status" in data:
            status = data["status"]
            if status in BUTTON_ACTION_MAP:
                self._properties["action"] = BUTTON_ACTION_MAP[status]
            else:
                self.log_warning('invalid status: {}' % status)

    def do_heartbeat(self, data):
        if "voltage" in data:
            self._properties["voltage"] = int(data["voltage"])
