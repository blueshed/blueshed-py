
define(
	["jquery",
	 "knockout",
     "blueshed/appl",
     "blueshed/connection",
     "blueshed/routes",
     "components/hello/main"], 
     
	function ($, ko, Appl, Connection, Routes, Hello) {
    	'use strict';

        ko.components.register("hello",Hello);    	
        
    	Appl.prototype.init = function(){
            this.title("Simple");
			this.connection = new Connection();
			this.service_status = ko.observable();
			this.loading = ko.observable(false);
			this.user = ko.observable();
			
            this.connection.broadcast.subscribe(function(msg){
				if(msg.signal == "user"){
					if(msg.ws_version){
						if(this.ws_version == null){
							this.ws_version = msg.ws_version;
						} else if(this.ws_version != msg.ws_version){
							location.reload();
							return;
						}
					}
					msg.message.permissions = ko.observableArray(msg.message.permissions);
					this.user(msg.message);
				} else if(msg.signal == "user updated"){
					if(ko.unwrap(this.user().id)==msg.message.id){
						this.user().permissions(msg.message.permissions);
						if(!this.has_permission(["user"])){
							document.location = "/logout";
						}
					}
				} else if(msg.signal == "_service_status_"){
					this.service_status(msg.message);
				}
			},this);

			this.is_admin = ko.pureComputed(function(){
				return this.has_permission(["admin"]);
			},this);
			this.connected = ko.pureComputed(function(){
				return this.connection.is_connected();
			},this);

            this.loading(true);
            this.routes = new Routes(this);
            this.routes.set_default(
            	this.routes.add_to_left_menu({
    				route:"hello",    // the name to pass to hasher
    				title:"Hello",    // the menu title
    				href:"",    	  // the href for the menu item
    				icon:null,        // the fa icon to set in menu item
    				action: function(){
    					this.component_params.args=arguments;
    					this.component_params.title="Hello World, again!"
    		        	this.component("hello");
    		        }.bind(this)
    			}));
    	}
    	
		var next_start = Appl.prototype.start;
    	Appl.prototype.start = function(){
    		this.routes.start();
			this.connection.connect(function(){
    			next_start.apply(this);
				this.loading(false);
			},this);
    	};

		Appl.prototype.has_permission = function(permissions){
			if(this.user() && this.user().permissions){
				var ps = ko.unwrap(this.user().permissions);
				for(var i=0; i<permissions.length;i++){
					if(ps.indexOf(permissions[i]) != -1){
						return true;
					}
				}
			}
			return false;
		};

    	return Appl;
	}
);