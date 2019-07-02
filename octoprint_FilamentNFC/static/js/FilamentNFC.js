/*
 * View model for OctoPrint-Filamentnfc
 *
 * Author: photo-mickey
 * License: AGPLv3
 */
$(function() {
    function FilamentnfcViewModel(parameters){
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
        //*******************************************************************
        material     = ko.observable();
        uid          = ko.observable();
        color        = ko.observable();
        weight       = ko.observable();
        balance      = ko.observable();
        diametr      = ko.observable();
        price        = ko.observable();
        vender       = ko.observable();
        density      = ko.observable();
        extMinTemp   = ko.observable();
        extMaxTemp   = ko.observable();
        bedMinTemp   = ko.observable();
        bedMaxTemp   = ko.observable();
        currency     = ko.observable();
        statusTimer  = ko.observable();
        statusRC522  = ko.observable();
        statusTag    = ko.observable();
        materialOptions = ko.observableArray([]);
        colorOptions    = ko.observableArray([]);
        currencySel     = ko.observable();
        self.LoginStateViewModel   = parameters[0];
        self.SettingsViewModel     = parameters[1];
        self.PrinterStateViewModel = parameters[2];
        self.settings = self.SettingsViewModel.settings;
        //*******************************************************************
        self.onAfterBinding = function(){
            currency(parameters[1].settings.plugins.FilamentNFC.currency());
            statusTimer("On");
            statusRC522("Offline");
            statusTag("No tag");
            self.systemMeas   = document.getElementById("rw-material");
            for(var i=0;i<materialList.length;i++){
                materialOptions.push(materialList[i]);
            }
            self.systemMeas   = document.getElementById("rw-color");
            for(var i=0;i<colorList.length;i++){
                colorOptions.push(colorList[i]);
            }
        }
        //*******************************************************************
        readSpoolSettings = function(){
            self.sendReadSpool();
        }

        writeSpoolSettings = function(){
            self.sendWriteSpool("writeSpool");
        }

        eraseSpoolSettings = function(){
            self.sendWriteSpool("eraseSpool");
        }

        setDefineSettings = function(){
            self.sendWriteSpool("setSpoolDefine");
        }

        stopTimer = function(){
            self.sendWriteSpool("stopTimer");
            statusTimer("Off");
        }

        startTimer = function(){
            self.sendWriteSpool("startTimer");
            statusTimer("On");
        }
        //*******************************************************************
        //********************************API********************************
        //*******************************************************************
        self.onDataUpdaterPluginMessage = function(plugin,message){
            if (plugin!="FilamentNFC"){
                return;
            }
            if (message==1){                        // RC522 communication ERROR!
                statusRC522("RC522 communication ERROR!");
            }
            if (message==2){                        // No nfc data from RC522
                statusRC522("Online");
                statusTag("No tag");
            }
            if (message==3){                        // New nfc data from RC522
                statusRC522("Online");
                statusTag("Tag detected");
                self.sendReadSpool();
            }
        }

        self.sendWriteSpool = function(command){
            if (command == "writeSpool"){
                bufWeight = 0;
                for(var i=0;i<materialList.length;i++){
                    if(material() == materialList[i]){
                        bufMaterial = i;
                    }
                }
                bufColor = 0;
                for(var i=0;i<colorList.length;i++){
                    if(color() == colorList[i]){
                        bufColor = i;
                    }
                }
                data = {"color"      : bufColor,
                        "material"   : bufMaterial,
                        "weight"     : weight(),
                        "balance"    : balance(),
                        "diametr"    : diametr()*100,
                        "price"      : price(),
                        "vender"     : vender(),
                        "density"    : density()*100,
                        "extMinTemp" : extMinTemp(),
                        "extMaxTemp" : extMaxTemp(),
                        "bedMinTemp" : bedMinTemp(),
                        "bedMaxTemp" : bedMaxTemp()
                       };
                console.log(data);
                OctoPrint.simpleApiCommand("FilamentNFC","writeSpool",data)
                    .done(function(response){
                    })
            }
            if (command == "eraseSpool"){
                data={};
                OctoPrint.simpleApiCommand("FilamentNFC","eraseSpool",data)
                    .done(function(response){
                    })
            }
            if (command == "stopTimer"){
                data={};
                OctoPrint.simpleApiCommand("FilamentNFC","stopTimer",data)
                    .done(function(response){
                    })
            }
            if (command == "startTimer"){
                data={};
                OctoPrint.simpleApiCommand("FilamentNFC","startTimer",data)
                    .done(function(response){
                    })
            }
            if (command == "setSpoolDefine"){
                data={};
                OctoPrint.simpleApiCommand("FilamentNFC","setSpoolDefine",data)
                    .done(function(response){
                    })
            }
        };

        self.sendReadSpool = function(data){
            OctoPrint.simpleApiGet("FilamentNFC")
                .done(function(response){
                    uid(response.uid);
                    material(materialList[response.material]);
                    color(colorList[response.color]);
                    weight(response.weight);
                    balance(response.balance);
                    diametr(response.diametr/100);
                    price(response.price);
                    vender(response.vender);
                    density(response.density/100);
                    extMinTemp(response.extMinTemp);
                    extMaxTemp(response.extMaxTemp);
                    bedMinTemp(response.bedMinTemp);
                    bedMaxTemp(response.bedMaxTemp);
                })
        };
    }
//*******************************************************************
//*******************************************************************
//*******************************************************************
    OCTOPRINT_VIEWMODELS.push({
        construct: FilamentnfcViewModel,
        dependencies: ["loginStateViewModel","settingsViewModel","printerStateViewModel"],
        elements: ["#NFC_bar"]
    });
});
