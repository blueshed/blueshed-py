require.config({
    urlArgs: "v=" +  (new Date()).getTime(),
    baseUrl: "static",
    paths: {
    	"augment":		  		"bower_components/augment.js/augment",
        "jquery" :        		"bower_components/jquery/dist/jquery",
        
        "knockout":		  		"bower_components/knockout/dist/knockout.debug",
        "knockout-mapping": 	"bower_components/knockout-mapping/knockout.mapping",
        "knockout-validation":  "bower_components/knockout-validation/dist/knockout.validation",
        "domready": 	  		"bower_components/requirejs-domready/domReady",
        "text":           		"bower_components/requirejs-text/text",
        	
        "signals":        "bower_components/js-signals/dist/signals",
        "hasher":         "bower_components/hasher/dist/js/hasher",
        "crossroads":     "bower_components/crossroads/dist/crossroads",

        "blueshed":		  "bower_components/blueshed-js/src"
    },
    shim: {},
    packages:[]
});

require(
	["knockout",
     "simple/appl",
     "domready!"], 
	function (ko, Appl) {
        "use strict";

        var appl = window.appl = new Appl();
        
        appl.start();
        
    	return appl;
	}
);
