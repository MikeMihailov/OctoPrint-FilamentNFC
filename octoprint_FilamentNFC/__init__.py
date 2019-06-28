# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin
import time
import os
import sys
from octoprint.events import eventManager, Events
from octoprint.server.util.flask import restricted_access
from octoprint.server import admin_permission
from octoprint.util import RepeatedTimer
import json
import flask
import logging

from .NFC_Comm import *
from .PlasticData import spool,material,colorStr
import RPi.GPIO as GPIO

class FilamentnfcPlugin(octoprint.plugin.StartupPlugin,
                        octoprint.plugin.TemplatePlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.SimpleApiPlugin,
                        octoprint.plugin.SettingsPlugin):
    interval = 3.0
    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(
                currency=5,
                scanPeriod=3.0
        )

    #def get_template_vars(self):
        #return dict(
                #currency=self._settings.get(["currency"]),
                #scanPeriod=self._settings.get(["scanPeriod"])
        #)

    def get_template_configs(self):
        return [
            dict(type="sidebar", template="FilamentNFC_sidebar.jinja2", custom_bindings=False),
            dict(type="settings", template="FilamentNFC_settings.jinja2", custom_bindings=False)
        ]

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self,data)
        self.scanPeriod=float(self._settings.get(["scanPeriod"]))
        self.restartTimer(self.scanPeriod)

    ##~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.info(">>Plugin is startup")
        self.scanPeriod=float(self._settings.get(["scanPeriod"]))
        GPIO.setwarnings(False)
        GPIO.cleanup()
        self.nfc=NFCmodule()
        if self.nfc.tag.status==0:
            self._logger.info(">>RC522 communication ERROR!")
        self.nfc.info=0
        self.nfc.tag.info=0
        self.startTimer(self.scanPeriod)

    def restartTimer(self,interval):
        if self.timer:
            self._logger.info(">>Stopping Timer...")
            self.timer.cancel()
            self.timer = None
            self.startTimer(interval)

    def startTimer(self,interval):
        self._logger.info(">>Starting Timer...")
        self.timer = RepeatedTimer(interval,self.updateData)
        self.timer.start()

    def updateData(self):
        self._logger.info(">>Timer!")
        if self.nfc.tag.status==1:
            res=self.nfc.readSpool()
            if res==1:
                self._plugin_manager.send_plugin_message(self._identifier,3)
            if res==0:
                self._plugin_manager.send_plugin_message(self._identifier,2)
                self.nfc.spool.clean()
        else:
            self._plugin_manager.send_plugin_message(self._identifier,1)
            
    

    ##~~ SimpleApiPlugin mixin
    def get_api_commands(self):
        return dict(
                    readSpool=["uid"]
        )

    def on_api_get(self, request):
        vender = self.nfc.spool.vender.replace('\x00','')
        list = {
                "uid"        : self.nfc.spool.uid,
                "material"   : material[self.nfc.spool.material],
                "color"      : colorStr[self.nfc.spool.color],
                "weight"     : self.nfc.spool.weight,
                "balance"    : self.nfc.spool.balance,
                "diametr"    : self.nfc.spool.diametr,
                "price"      : self.nfc.spool.price,
                "vender"     : vender,
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