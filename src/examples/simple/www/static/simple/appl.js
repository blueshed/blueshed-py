
define(
	["knockout",
     "blueshed/main",
     "blueshed/connection",
     "blueshed/components/inspector/store",
     "blueshed/components/inspector/main",
     "blueshed/components/modeling/main",
     "components/hello/main"], 
     
	function (ko, Appl, Connection, Store,
			  InspectorPanel, ModelingPanel, Hello) {
    	'use strict';

        ko.components.register("hello",Hello);   
        ko.components.register("inspector-panel",InspectorPanel);
        ko.components.register("modeling-panel",ModelingPanel); 	
        
    	Appl.prototype.init = function(){
            this.title("Simple");
			this.connection = new Connection();
			this.store = new Store(this.connection, this.error, this.notify);
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
					this.store.init(msg.model);
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
            this.init_routes();
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
            this.add_service_menu("Inspector","inspector-panel","inspector/:id:","","#/inspector");
            this.add_service_menu("Modeling","modeling-panel","modeling/:id:","","#/modeling");
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
		
		Appl.prototype.save_model = function(json_model, sqla_model){
			this.connection.send({
				action: "save_model",
				args:{json_model:json_model,sqla_model:sqla_model}
			},function(response){
				if(response.error){
					this.error(response.error);
					return;
				}
				this.ws_version = -1; // will reload on reconnect
			}.bind(this));
		};

    	return Appl;
	}
);