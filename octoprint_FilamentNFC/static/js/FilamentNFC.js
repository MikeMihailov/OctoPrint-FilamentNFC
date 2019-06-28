/*
 * View model for OctoPrint-Filamentnfc
 *
 * Author: photo-mickey
 * License: AGPLv3
 */
$(function() {
    function FilamentnfcViewModel(parameters) {
        var self = this;
        
        currencyList = ["\u20BD",
                        "\u20B4",
                        "\u043B",
                        "\u006B",
                        "\u005A",
                        "\u17DB",
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
        self.material     = ko.observable();
        self.status       = ko.observable();
        self.uid          = ko.observable();
        self.color        = ko.observable();
        self.weight       = ko.observable();
        self.balance      = ko.observable();
        self.diametr      = ko.observable();
        self.price        = ko.observable();
        self.vender       = ko.observable();
        self.density      = ko.observable();
        self.extMinTemp   = ko.observable();
        self.extMaxTemp   = ko.observable();
        self.bedMinTemp   = ko.observable();
        self.bedMaxTemp   = ko.observable();
        self.currency     = ko.observable();
        self.currencyN    = ko.observable();
        self.LoginStateViewModel   = parameters[0];
        self.SettingsViewModel     = parameters[1];
        self.PrinterStateViewModel = parameters[2];
        self.nfcStatus = 0;
        self.settings = self.SettingsViewModel.settings;
        //*******************************************************************
        self.onAfterBinding = function() {
            n = parameters[1].settings.plugins.FilamentNFC.currency()
            self.currencyN(n);
            self.currency(currencyList[n]);

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
        /*
        self.readSpool = function () {
            self.sendReadSpool();
        }
        
        self.readSpoolSettings = function(){
        }
        
        self.writeSpoolSettings = function(){
        }
        
        self.eraseSpoolSettings = function(){
        }
        */
        //*******************************************************************
        //********************************API********************************
        //*******************************************************************
        self.onDataUpdaterPluginMessage = function(plugin, message){
            if (plugin!="FilamentNFC"){
                return;
            }
            if (message==1){                        // RC522 communication ERROR!
                self.status("RC522 communication ERROR!");
                self.nfcStatus = 0
            }
            if (message==2){                        // New nfc data from RC522
                self.status("Online");
                self.nfcStatus = 1
            }
            if (message==3){                        // New nfc data from RC522
                self.sendReadSpool();
            }
        }
        
        self.sendReadSpool = function(data) {
            OctoPrint.simpleApiGet("FilamentNFC")
                .done(function(response) {
                    self.status("Online");
                    self.uid(response.uid);
                    self.material(response.material);
                    self.color(response.color);
                    self.weight(response.weight);
                    self.balance(response.balance);
                    self.diametr(response.diametr/100);
                    self.price(response.price);
                    self.vender(response.vender);
                    self.density(response.density/100);
                    self.extMinTemp(response.extMinTemp);
                    self.extMaxTemp(response.extMaxTemp);
                    self.bedMinTemp(response.bedMinTemp);
                    self.bedMaxTemp(response.bedMaxTemp);
                })
        };
    }


    OCTOPRINT_VIEWMODELS.push({
        construct: FilamentnfcViewModel,
        dependencies: ["loginStateViewModel","settingsViewModel","printerStateViewModel"],
        elements: ["#NFC_bar"]
    });
});
