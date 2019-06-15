# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin
import time
import os
import sys
from octoprint.events import eventManager, Events
from octoprint.server.util.flask import restricted_access
from octoprint.server import admin_permission
import json
import flask
import logging

from .NFC_Comm import *
import RPi.GPIO as GPIO

class FilamentnfcPlugin(octoprint.plugin.StartupPlugin,
                        octoprint.plugin.TemplatePlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.SimpleApiPlugin,
                        octoprint.plugin.SettingsPlugin):
    ##~~ SettingsPlugin mixin
    def on_after_startup(self):
        self._logger.info(">>Filament NFC is startup")
        GPIO.setwarnings(False)
        GPIO.cleanup()
        self.nfc=NFCmodule()
        self.nfc.DEBUG=0

    ##~~ SimpleApiPlugin mixin
    def get_api_commands(self):
        return dict(
                    readSpool=["uid"]
        )

    def on_api_get(self, request):
        self.nfc.readSpool()
        list = {
                "uid"        : self.nfc.spool.uid,
                "material"   : self.nfc.spool.material,
                "color"      : self.nfc.spool.color,
                "weight"     : self.nfc.spool.weight,
                "balance"    : self.nfc.spool.balance,
                "diametr"    : self.nfc.spool.diametr,
                "price"      : self.nfc.spool.price,
                "vender"     : self.nfc.spool.vender,
                "density"    : self.nfc.spool.density,
                "extMinTemp" : self.nfc.spool.extMinTemp,
                "extMaxTemp" : self.nfc.spool.extMaxTemp,
                "bedMinTemp" : self.nfc.spool.bedMinTemp,
                "bedMaxTemp" : self.nfc.spool.bedMaxTemp
        }
        return json.dumps(list)










    def on_api_command(self, command, data):
        if command == 'readSpool':
            self.nfc.readSpool()
            parameter = self.nfc.spool.uid;
            self._plugin_manager.send_plugin_message(self._identifier, self.nfc.spool.vender)



    ##~~ AssetPlugin mixin
    def get_assets(self):
        return dict(
            js=["js/FilamentNFC.js"],
            css=["css/FilamentNFC.css"],
            less=["less/FilamentNFC.less"]
        )

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            FilamentNFC=dict(
                displayName="FilamentNFC",
                displayVersion=self._plugin_version,
                # version check: github repository
                type="github_release",
                user="photo-mickey",
                repo="OctoPrint-Filamentnfc",
                current=self._plugin_version,
                # update method: pip
                pip="https://github.com/photo-mickey/OctoPrint-Filamentnfc/archive/{target_version}.zip"
            )
        )
__plugin_name__ = "FilamentNFC"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FilamentnfcPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }