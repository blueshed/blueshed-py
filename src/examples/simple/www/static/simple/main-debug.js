require.config({
    urlArgs: "v=" +  (new Date()).getTime(),
    baseUrl: "static",
    paths: {
    	"augment":		  		"bower_components/augment.js/augment",
        "jquery" :        		"bower_components/jquery/dist/jquery",        
        "jquery-ui" :           "bower_components/jquery-ui/ui",
        
        "bootstrap":        	    "bower_components/bootstrap/dist/js/bootstrap",
        "bootstrap-notify":  	    "bower_components/bootstrap-notify/js/bootstrap-notify",
        "bootstrap-colorselector":  "bower_components/bootstrap-colorselector/lib/bootstrap-colorselector-0.2.0/js/bootstrap-colorselector",
        "bootstrap-datetimepicker": "bower_components/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min",

        "knockout":		  		"bower_components/knockout/dist/knockout.debug",
        "knockout-mapping": 	"bower_components/knockout-mapping/knockout.mapping",
        "knockout-validation":  "bower_components/knockout-validation/dist/knockout.validation",   
        "knockout-switch-case": "bower_components/knockout-switch-case/knockout-switch-case",
        "knockout-sortable":    "bower_components/knockout-sortable/build/knockout-sortable",   

        "domready": 	  		"bower_components/requirejs-domready/domReady",
        "text":           		"bower_components/requirejs-text/text",

        "dropzone":             "bower_components/dropzone/dist/dropzone-amd-module",
                
        "aws-sdk":              "bower_components/aws-sdk/dist/aws-sdk",
        "aws-config":           "bridge/aws-config",
                	
        "signals":        "bower_components/js-signals/dist/signals",
        "hasher":         "bower_components/hasher/dist/js/hasher",
        "crossroads":     "bower_components/crossroads/dist/crossroads",

        "select2":        "bower_components/select2/dist/js/select2",
        
        "moment":         "bower_components/moment/min/moment.min",
        "numeral":        "bower_components/numeral/numeral",

        "blueshed":		  "bower_components/blueshed-js/src",
            
        'jszip':          'bower_components/jszip/jszip',
        'viz':            'viz'
    },
    shim: {
        "bootstrap": {
            deps: ["jquery"]
        },
        "bootstrap-notify": {
            deps: ["bootstrap"]
        },
        "bootstrap-colorselector": {
            deps: ["bootstrap"]
        },
        "aws-sdk" : {
            exports: 'AWS'
        },
        "viz": {
        	exports: "Viz"
        },
        "jszip": {
        	exports: "JSZip"
        }
    },
    packages:[{
        name: "codemirror",
        location: "bower_components/codemirror",
        main: "lib/codemirror"
    }]
});

require(
	["knockout",
     "simple/appl",
     "blueshed/templates/extra",
     "domready!"], 
	function (ko, Appl) {
        "use strict";

        var appl = window.appl = new Appl();
        
        appl.start();
        
    	return appl;
	}
);
