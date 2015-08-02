
define(
	["knockout",
	 "text!/config",
     "blueshed/main",
     "blueshed/connection",
     "blueshed/store",
     "blueshed/utils/random-str",
     "blueshed/components/inspector/main",
     "blueshed/components/modeling_v2/main",
     "blueshed/components/s3-browser/main",
     "components/change-password/main",
     "components/edit-profile/main",
     "components/online-users/main",
     "components/test/main",
     "components/notes/main",
     "components/hello/main"], 
     
	function (ko, CONFIG, Appl, Connection, Store, randomStr,
			  InspectorPanel, 
			  ModelingPanel, 
			  S3Browser,
			  ChangePassword,
			  EditProfile,
			  OnlineUsers,
			  TestPanel,
			  NotesPanel,
			  HelloPanel) {
    	'use strict';

        ko.components.register("hello-panel",HelloPanel);   
        ko.components.register("test-panel",TestPanel);     
        ko.components.register("notes-panel",NotesPanel);   
        ko.components.register("inspector-panel",InspectorPanel);
        ko.components.register("modeling-panel",ModelingPanel); 
        ko.components.register("s3-browser",S3Browser);
        ko.components.register("change-password",ChangePassword);
        ko.components.register("edit-profile",EditProfile);
        ko.components.register("online-users",OnlineUsers);	
        
        CONFIG = JSON.parse(CONFIG);
        
    	Appl.prototype.init = function(){
            this.title("Simple");
			this.connection = new Connection();
			this.store = new Store(this.connection, this.error, this.notify);
			this.service_status = ko.observable();
			this.loading = ko.observable(false);
			this.user = ko.observable();
			
			// initialize routes
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
    		        	this.component("hello-panel");
    		        }.bind(this)
    			}));
            this.routes.add_to_right_menu({component_name:'online-users',appl:this});

            this.add_menu_left("Test",'test-panel',"test","","#/test");
            this.add_menu_left("Notes",'notes-panel',"notes/:id:","","#/notes");
            this.add_service_menu("Inspector","inspector-panel","inspector/:id:","","#/inspector");
            this.add_service_menu("Modeling","modeling-panel","modeling/:id:","","#/modeling");
            this.add_page("S3 Browser",function(){
            	this.component_params.AWS_AccessKeyId=CONFIG.aws_access_key_id;
            	this.component_params.AWS_SecretAccessKey=CONFIG.aws_secret_access_key;
            	this.component_params.AWS_BucketName=CONFIG.s3_bucket;
            	this.component_params.AWS_Region=CONFIG.s3_bucket_region;
            	this.component_params.AWS_Prefix="";
            	this.component_params.s3_base_url=CONFIG.s3_base_url;
            	this.component_params.s3_upload_url=CONFIG.s3_upload_url;
    			this.component_params.args=arguments;
        		this.component("s3-browser");
        	}.bind(this),"s3","#/s3","fa fa-cloud");
            
			this.add_page("-");
			this.add_page("Edit Profile",this.edit_profile.bind(this));
			this.add_page("Change Password",this.change_password.bind(this));
			
			
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
					this.config = msg.ws_config;
					this.store.init(msg.model, msg.methods);
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
				} else if(msg.signal == "echo"){
					this.notify(msg.message,"info",".top-left");
				}
			},this);

			this.is_admin = ko.pureComputed(function(){
				return this.has_permission(["admin"]);
			},this);
			this.connected = ko.pureComputed(function(){
				return this.connection.is_connected();
			},this);

            this.loading(true);
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
		
		Appl.prototype.save_preferences = function(namespace,values){
			if(!this.user.preferences){
				this.user.preferences = {};
			}
			this.user.preferences[namespace]=values;
			this.connection.send({action:"save_prefernces", args:{preferences:this.user.preferences}});
		};
		
        Appl.prototype.change_password = function(){
        	this.open_dialog("change-password", {appl:this});
        };
		
        Appl.prototype.edit_profile = function(){
        	this.open_dialog("edit-profile", {appl:this, user: this.user()});
        };
		
		Appl.prototype.fetch_model = function(callback,err_back){
			this.connection.send({
				action: "fetch_model"
			},function(response){
				if(response.result){
					var new_models = JSON.parse(response.result);
					callback(new_models);
				}
			}.bind(this),err_back);
		};
		
		Appl.prototype.photo_args = function(prefix, photo){
        	var args = {
        		url: "/images/",
        		maxFiles:1,
        		createImageThumbnails: true,
				success: function(file,response){
					if(response.error){
						this.error(response.error);
						return;
					}
					photo(response.result.file.thumb);
				}.bind(this),
				sending: function(file, xhr, formData) {
					formData.append("prefix", prefix + "/" + randomStr(8));
				}.bind(this),
				complete:function(file){
					this.removeFile(file);
				},
				dictDefaultMessage:"Drop files here or 'click' to change photo"
        	};
        	return args;
		};
        
        Appl.prototype.open_photo = function(src){
        	src = ko.unwrap(src);
    		src = src.replace("/thumbnail.","/original.");
    		this.open_dialog("photo-dialog",{src:src,title:title});
        };

    	return Appl;
	}
);