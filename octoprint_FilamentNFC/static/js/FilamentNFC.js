/*
 * View model for OctoPrint-Filamentnfc
 *
 * Author: photo-mickey
 * License: AGPLv3
 */
$(function() {
    function FilamentnfcViewModel(parameters) {
        var self = this;
        
        systemMeasList = ["Systeme Internationa", "Imperial system"]
        currencyList = ["\u20BD",
                        "\u20B4",
                        "\u043B",
                        "\u006B",
                        "\u005A",
                        "\u17DB",
                        "\u0016",
                        "\u0192",
                        "\u20A1",
                        "\u0051",
                        "\u20AE",
                        "\u004D",
                        "\u20A8",
                        "\u20A6",
                        "\u0024",
                        "\u007A",
                        "\u20AC",
                        "\u00A3",
                        "\u0043",
                        "\u00A5",
                        "\u00A5",
                        "\u20AB",
                        "\u20A9",
                        "\u0E3F",
                        "\u20AD"
                       ]
        materialList = ['',
                        'ABS',
                        'PLA',
                        'Watson',
                        'HiPS',
                        'PETG',
                        'Nylon',
                        'ASA',
                        'PVA',
                        'PETT',
                        'PET',
                        'TPU',
                        'TPE',
                        'PC',
                        'PP',
                        'WOOD'
                       ]
        colorList =['',
                    'white',
                    'black',
                    'light gray',
                    'gray',
                    'red',
                    'green',
                    'blue',
                    'yellow',
                    'orange',
                    'brown',
                    'purple',
                    'emerald',
                    'skiey',
                    'coral',
                    'rose',
                    'chocolate',
                    'gold',
                    'krem',
                    'lime green',
                    'light blue',
                    'natural'
                   ]
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
            
            self.systemMeas   = document.getElementById("settings-systemMeasurement");
            for(var i=0;i<systemMeasList.length;i++){
                self.systemMeas.options[i] = new Option(systemMeasList[i],String(i));
            }
            
            self.systemMeas   = document.getElementById("settings-currency");
            for(var i=0;i<currencyList.length;i++){
                self.systemMeas.options[i] = new Option(currencyList[i],String(i));
            }
            
            self.systemMeas   = document.getElementById("rw-material");
            for(var i=0;i<materialList.length;i++){
                self.systemMeas.options[i] = new Option(materialList[i],String(i));
            }
            
            self.systemMeas   = document.getElementById("rw-color");
            for(var i=0;i<colorList.length;i++){
                self.systemMeas.options[i] = new Option(colorList[i],String(i));
            }
        }
        //*******************************************************************
        self.readSpool = function () {
            self.sendReadSpool();
        }
        //*******************************************************************
        //********************************API********************************
        //*******************************************************************
        self.onDataUpdaterPluginMessage = function(plugin, message){
            if (plugin != "FilamentNFC") return;
            if (message){
                self.sendReadSpool();
            }
        }
        
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
