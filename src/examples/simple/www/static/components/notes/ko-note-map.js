define(
    ["require",
     "jquery",
     "knockout",
     "blueshed/notify"],
    function(require,$,ko,Notify){

    	var markers = {};
    	var loaded = ko.observable(false);
    	
    	require(["text!/config"],function(config_json){
    		var config = JSON.parse(config_json);
    		
    		require(["async!http://maps.googleapis.com/maps/api/js?key="+config.google_key], function(){
    	

    	var readOnlyOptions = {
		    streetViewControl: false,
            mapTypeId: google.maps.MapTypeId.SATELLITE,
			disableDefaultUI: true,
			draggable: false,
			scrollwheel: false,
        };
    	
    	var editableOptions = {
		    streetViewControl: false,
            mapTypeId: google.maps.MapTypeId.SATELLITE,
			disableDefaultUI: false,
			draggable: true,
			scrollwheel: true,
        };
    	
         function code_address(value, cb) {
        	 value = ko.unwrap(value);
        	 if(value){
	        	 var geocoder = new google.maps.Geocoder();
	        	 geocoder.geocode( { 'address': value }, function(results, status) {
	                if (status == google.maps.GeocoderStatus.OK) {
	                    cb(results[0].geometry.location);
	                } else {
	                    Notify.notify("Geocode error: " + status, "error");
	                }
	            });
        	 }
        };
        
        function geo_locate(map){
        	var that = this;
        	if (navigator.geolocation){
				navigator.geolocation.getCurrentPosition(function(position){
					var loc = new google.maps.LatLng(
							position.coords.latitude, 
							position.coords.longitude, 
							noWrap=false);
					map.setCenter(loc);
				});
		    }
			else{
				Notify.error("Geolocation is not supported by this browser.");
			}
        };
        
        function make_map(widget, element, valueAccessor, allBindings, viewModel, bindingContext){
        	var editable = $(element).attr("editable") == "true";

            if(editable === true){
             	$(element).css("height",$(element).width()+"px");
            }
            var sub = null;
             
            var latlng = new google.maps.LatLng(widget.lat(),widget.lng());
            var mapOptions = $.extend({
                center: latlng,
                zoom: widget.zoom() || 8,
                mapTypeId: widget.map_type() || google.maps.MapTypeId.SATELLITE
            }, (editable === true ? editableOptions: readOnlyOptions));
            var map = new google.maps.Map(element, mapOptions);
            
            var marker = null;
            if(editable === true){
                google.maps.event.addListener(map, 'center_changed', function() {
                    var c = map.getCenter();
                    widget.lat(c.lat());
                    widget.lng(c.lng());
                });
                google.maps.event.addListener(map, 'zoom_changed', function() {
                	widget.zoom(map.getZoom());
                });
                google.maps.event.addListener(map, 'maptypeid_changed', function() {
                	widget.map_type(map.getMapTypeId());
                });
                
            	marker = new google.maps.Marker({
                    map: map,
                    position: latlng
                });
            	markers["e" + widget.id()]=marker;
            	
            } else {
            	marker = new google.maps.Marker({
                    map: map,
                    position: latlng
                });
            	markers[widget.id()]=marker;
            }
            
            $(element).on("wd-resize",function(){
            	google.maps.event.trigger(element, 'resize');
        		marker.setPosition(new google.maps.LatLng(widget.lat(),widget.lng()));
        		marker.getMap().setCenter(marker.getPosition());
        		marker.getMap().setZoom(widget.zoom() || 8);
        		marker.getMap().setMapTypeId(widget.map_type() || google.maps.MapTypeId.SATELLITE);
            });
            

            var address = $(element).data("_address_");
            if(address._sub){
            	address._sub.dispose();
            }
            if(editable === true){
            	sub = address.subscribe(function(value){
            		code_address(value,function(loc){
            			map.setCenter(loc);
            		});
            	});
            }
            
            $(element).data("_map_",map);
            
			ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        		$(element).data("_map_",null);
				$(element).off("wd-resize");
				marker.setMap(null);
                if(editable === true){
                	if(sub){
						sub.dispose();
					}
            		$(element).data("_address_",null);
                	delete markers["e" + widget.id()];
                } else {
                	delete markers[widget.id()];
                }
	            delete map;
	        });
			
			return map;
        }


        ko.bindingHandlers['note-map'] = {
            init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
                var widget = ko.unwrap(valueAccessor());
                
                var address = ko.observable();
        		$(element).data("_address_",address);
        		
                if(widget.location()){
                	make_map(widget, element, valueAccessor, allBindings, viewModel, bindingContext);
//                	console.log("made map on init");
                } else {
                	address._sub = address.subscribe(function(value){
                		code_address(value,function(loc){
	                		widget.lat(loc.lat());
	                		widget.lng(loc.lng());
                		});
                	});
                }
            },
            update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            	var widget = ko.unwrap(valueAccessor());
            	if(widget.location()){
	            	var $element = $(element);
	            	var map = $element.data("_map_");
	            	if(!map){
	            		make_map(widget, element, valueAccessor, allBindings, viewModel, bindingContext);
//	            		console.log("made map on update");
	            	} 
	            	$element.trigger("wd-resize");
            	}
            }
        };
        

			loaded(google);
		
    		});// end google
    	});// end config
        
    	return loaded;
    }
);