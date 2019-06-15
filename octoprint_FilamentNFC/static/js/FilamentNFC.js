/*
 * View model for OctoPrint-Filamentnfc
 *
 * Author: photo-mickey
 * License: AGPLv3
 */
$(function() {
    function FilamentnfcViewModel(parameters) {
        var self = this;
        //*******************************SPOOL*******************************
        function spool () {
            this.uid        = 0;				// UID of spool NFC 
            this.material   = 1;				// ABS as default (from matirial list)
            this.color      = 1;				// White as default (..)
            this.weight     = 1000;				// gr (1kg as default)
            this.balance    = this.weight;		// gr (100% as default)
            this.diametr    = 175;				// mm*10^-2
            this.price      = 1200;				// in rus rub as default (The most popular currency in the world ofcause)
            this.vender     = 'BestFilament';	// text line of 16 char max
            this.density    = 105;				// gr/cm^3 *10^-2
            this.extMinTemp = 220;				// Extruder minimum temperature, 'C
            this.extMaxTemp = 270;				// Extruder maximum temperature, 'C
            this.bedMinTemp = 90;				// Bed minimum temperature, 'C
            this.bedMaxTemp = 110;				// Bed maximum temperature, 'C
        }
        //*******************************PARAM*******************************
        self.allSettings  = parameters[0];
        self.loginState   = parameters[1];
        self.printerState = parameters[2];
        self.confirmation = undefined;
        self.spool        = new spool();
        //*******************************************************************
        self.onAfterBinding = function() {
            self.confirmation = $("#confirmation");
            self.message      = document.getElementById("message");
            // Spool:
            self.uid          = document.getElementById("uid");
            self.material     = document.getElementById("material");
            self.color        = document.getElementById("color");
            self.weight       = document.getElementById("weight");
            self.balance      = document.getElementById("balance");
            self.diametr      = document.getElementById("diametr");
            self.price        = document.getElementById("price");
            self.vender       = document.getElementById("vender");
            self.density      = document.getElementById("density");
            self.extMinTemp   = document.getElementById("extMinTemp");
            self.extMaxTemp   = document.getElementById("extMaxTemp");
            self.bedMinTemp   = document.getElementById("bedMinTemp");
            self.bedMaxTemp   = document.getElementById("bedMaxTemp");
        }
        //*******************************************************************
        self.showMessage = function (data) {
            self.confirmation.modal("show");
            self.message.textContent = data;
        }
        //*******************************************************************
        self.readSpool = function () {
            self.sendReadSpool();
            //self.showMessage(">>I have read NFC");
            //self.uid.textContent = "0";
            //self.material.textContent = "DONE";
        }
        //*******************************************************************
        //********************************API********************************
        //*******************************************************************
self.onDataUpdaterPluginMessage = function(plugin, message){
self.vender.textContent = message;
}

        /*
        self.sendReadSpool = function(data) {
            var payload = {"ip": "someIp"};
            OctoPrint.simpleApiCommand("FilamentNFC", "readSpool", payload)
                .done(function(response) {
                    var i = 0;
                })
        };
		*/
        self.sendReadSpool = function(data) {
            OctoPrint.simpleApiGet("FilamentNFC")
                .done(function(response) {
                    self.uid.textContent        = response.uid;
                    self.material.textContent   = response.material;
                    self.color.textContent      = response.color;
                    self.weight.textContent     = response.weight;
                    self.balance.textContent    = response.balance;
                    self.diametr.textContent    = response.diametr;
                    self.price.textContent      = response.price;
                    self.vender.textContent     = response.vender;
                    self.density.textContent    = response.density;
                    self.extMinTemp.textContent = response.extMinTemp;
                    self.extMaxTemp.textContent = response.extMaxTemp;
                    self.bedMinTemp.textContent = response.bedMinTemp;
                    self.bedMaxTemp.textContent = response.bedMaxTemp;
                })
        };
		/*
        self.sendReadSpool = function(data) {
            $.ajax({
                url: API_BASEURL + "plugin/FilamentNFC",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "readSpool",
                    ip: "Some ip"
                }),
                contentType: "application/json; charset=UTF-8"
            });
        };
		*/
        //*******************************************************************
		/*
        self.sendWriteSpool = function(data) {
            $.ajax({
                url: API_BASEURL + "plugin/filamentnfc",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "readSpool",
                }),
                contentType: "application/json; charset=UTF-8"
            });
        };
		*/
        //*******************************************************************
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: FilamentnfcViewModel,
        dependencies: ["loginStateViewModel", "settingsViewModel","printerStateViewModel"],
        elements: ["#NFC_bar"]
    });
});
