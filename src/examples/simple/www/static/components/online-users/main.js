define(["knockout",
        "text!./main-tmpl.html"],
	function(ko, main_tmpl){
	
		function OnlineUsers(params){
			this.appl = params.appl;
			this.users = ko.observableArray();
			this.sub = this.appl.service_status.subscribe(function(value){
				this.users.removeAll();
				if(value){
					value.clients.map(function(id){
						this.users.push(this.appl.store.get_person(id));
					},this);
				}
			},this);
		}
		
		OnlineUsers.prototype.dispose = function(){
			this.sub.dispose();
		};
		
		OnlineUsers.prototype.edit_user = function(user){
			this.appl.open_dialog("edit-profile", {appl:this.appl, user: ko.toJS(user)});
		};
		
		return {
			viewModel: OnlineUsers,
			template: main_tmpl
		};
	
	}
);