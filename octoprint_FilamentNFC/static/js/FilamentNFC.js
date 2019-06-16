/*
 * View model for OctoPrint-Filamentnfc
 *
 * Author: photo-mickey
 * License: AGPLv3
 */
$(function() {
    function FilamentnfcViewModel(parameters) {
        var self = this;
        //*******************************PARAM*******************************
        self.allSettings  = parameters[0];
        self.loginState   = parameters[1];
        self.printerState = parameters[2];
        //*******************************************************************
        self.onAfterBinding = function() {
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
        self.readSpool = function () {
            self.sendReadSpool();
        }
        //*******************************************************************
        //********************************API********************************
        //*******************************************************************
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
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: FilamentnfcViewModel,
        dependencies: ["loginStateViewModel", "settingsViewModel","printerStateViewModel"],
        elements: ["#NFC_bar"]
    });
});
