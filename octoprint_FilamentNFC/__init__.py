# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin
import NFC_Comm
import signal
import RPi.GPIO as GPIO
    
class FilamentnfcPlugin(octoprint.plugin.SettingsPlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.TemplatePlugin):

	##~~ SettingsPlugin mixin
	def on_after_startup(self):
		self._logger.info("Filament NFC (more: %s)" % self._settings.get(["material"]))
        GPIO.setwarnings(False)
        signal.signal(signal.SIGINT, end_read)  # Hook the SIGINT
        GPIO.cleanup()
        self.NFC       = NFC()
        self.NFC.DEBUG = 0;

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js  =["js/FilamentNFC.js"    ],
			css =["css/FilamentNFC.css"  ],
			less=["less/FilamentNFC.less"]
		)
    
    def on_api_command(self, command, data):
        if command == 'readNFC':
            self.NFC.readSpool()
        return 0
            
            
	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
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


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "FilamentNFC"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = FilamentnfcPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

