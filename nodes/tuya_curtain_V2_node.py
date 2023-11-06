"""
Polyglot v3 node server
Copyright (C) 2023 Steven Bailey
MIT License
Version 1.0.1 Jun 2023
"""
import asyncio
import colorsys
import udi_interface
import time
import json
from tuya_bulb_control import Bulb
from tuya_connector import (
    TuyaOpenAPI,)


LOGGER = udi_interface.LOGGER


class CurtainNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, new_id, deviceid, apiAccessId, apiSecret, apiEndpoint, apiRegion):
        super(CurtainNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address, name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.new_id = new_id
        self.deviceid = deviceid
        self.DEVICELED_ID = deviceid
        self.apiAccessId = apiAccessId
        self.ACCESS_ID = apiAccessId
        self.apiSecret = apiSecret
        self.ACCESS_KEY = apiSecret
        self.apiEndpoint = apiEndpoint
        self.API_ENDPOINT = apiEndpoint
        self.apiRegion = apiRegion
        self.API_REGION = apiRegion
        self.SwStat(self)

    # Set Modes
    def modeOn(self, command):
        API_ENDPOINT = self.API_ENDPOINT
        ACCESS_ID = self.ACCESS_ID
        ACCESS_KEY = self.ACCESS_KEY
        DEVICELED_ID = self.DEVICELED_ID
        openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()
        self.modeOn = int(command.get('value'))
        self.setDriver('GV4', self.modeOn)
        # Stop
        if self.modeOn == 0:
            commands = {'commands': [{'code': 'control', 'value': 'stop'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICELED_ID), commands)
            LOGGER.info('Colour')
            time.sleep(.1)
            self.SwStat(self)
        # Open
        elif self.modeOn == 1:
            commands = {'commands': [{'code': 'control', 'value': 'open'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICELED_ID), commands)
            LOGGER.info('Scene')
            time.sleep(.1)
            self.SwStat(self)
        # Close
        elif self.modeOn == 2:
            commands = {'commands': [{'code': 'control', 'value': 'close'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICELED_ID), commands)
            time.sleep(.5)
            self.SwStat(self)
        # Continue
        elif self.modeOn == 3:
            commands = {'commands': [{'code': 'control', 'value': 'continue'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICELED_ID), commands)
            time.sleep(.5)
            self.SwStat(self)
            
    # Set Modes
    def modeDir(self, command):
        API_ENDPOINT = self.API_ENDPOINT
        ACCESS_ID = self.ACCESS_ID
        ACCESS_KEY = self.ACCESS_KEY
        DEVICELED_ID = self.DEVICELED_ID
        openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()
        self.modeOn = int(command.get('value'))
        self.setDriver('GV5', self.modeOn)
        # Forward
        if self.modeDir == 0:
            commands = {'commands': [{'code': 'control_back_mode', 'value': 'forward'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICELED_ID), commands)
            LOGGER.info('Colour')
            time.sleep(.1)
            self.SwStat(self)
        # Back
        elif self.modeDir == 1:
            commands = {'commands': [{'code': 'control_back_mode', 'value': 'back'}]}
            openapi.post(
                '/v1.0/iot-03/devices/{}/commands'.format(DEVICELED_ID), commands)
            LOGGER.info('Scene')
            time.sleep(.1)
            self.SwStat(self)

    # Percent Control
    def setDim(self, command):
        API_ENDPOINT = self.API_ENDPOINT
        ACCESS_ID = self.ACCESS_ID
        ACCESS_KEY = self.ACCESS_KEY
        DEVICELED_ID = self.DEVICELED_ID
        openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()
        self.SwStat(self)

        ivr_one = 'percent'
        percent = int(command.get('value'))

        def set_percent(self, command):
            percent = int(command.get('value')) #*10
        if percent < 0 or percent > 100:
            LOGGER.error('Invalid Level {}'.format(percent))
        else:
            commands = {'commands': [{'code': 'percent_control', 'value': int(percent)}]} #*10
            openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICELED_ID), commands)
            LOGGER.info('percent Setpoint = ' + str(percent) + ' Level')

    def SwStat(self, command):
        API_ENDPOINT = self.API_ENDPOINT
        ACCESS_ID = self.ACCESS_ID
        ACCESS_KEY = self.ACCESS_KEY
        DEVICELED_ID = self.DEVICELED_ID
        openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()

        response1 = openapi.get(
            "/v1.0/iot-03/devices/{}".format(DEVICELED_ID) + "/status/")  # DEVICE_ID
        LOGGER.info(response1)
        for i in response1['result'][0:1]:
            self.setDriver('GV3', i['value'])
            LOGGER.info(i['value'])
            
        #### Device Online Status
        response = openapi.get("/v1.0/devices/{}".format(DEVICELED_ID))
        LOGGER.info(response['result']['online'])
        if response['result']['online'] == True:
            LOGGER.info(response['result']['online'])
            self.setDriver('ST', 1)
        if response['result']['online'] == False:
            LOGGER.info(response['result']['online'])
            self.setDriver('ST', 0)
        else:
            pass

    def poll(self, polltype):
        if 'longPoll' in polltype:
            LOGGER.debug('longPoll (node)')
        else:
            self.SwStat(self)
            self.query(self)
            LOGGER.debug('shortPoll (node)')

    def query(self, command=None):
        self.SwStat(self)
        self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2, 'name': 'Online'},
        {'driver': 'GV3', 'value': 0, 'uom': 51, 'name': 'Curtain Level'},
        {'driver': 'GV4', 'value': 0, 'uom': 25, 'name': 'Curtain Mode'},
        {'driver': 'GV5', 'value': 0, 'uom': 25, 'name': 'Curtain Direction'},
    ]

    id = 'curtain2'

    commands = {
        'MODECUR': modeOn,
        'MODEDIR': modeDir,
        'STLVL': setDim,
        'QUERY': query,
    }
