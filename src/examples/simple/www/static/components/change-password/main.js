define(["knockout","text!./main-tmpl.html"],
	function(ko, main_tmpl){
	
		function Dialog(params){
			this.appl = params.appl;
			this.old = ko.observable();
			this.new_1 = ko.observable();
			this.new_2 = ko.observable();
			this.error = ko.observable();
			
			this.isValid = ko.computed(function(){
				return this.old() && this.new_1() && 
					   this.new_1().length > 4 &&
					   (this.new_1()==this.new_2());
			},this);		
		}
		
		Dialog.prototype.submit = function(){
			this.appl.connection.send({
				action:'change_password',
				args:{
					old_password:this.old(),
					new_password:this.new_1() 
				} 
			}, 
			function(response){
				if(response.error){
					this.error(response.error);
				} else {
					this.appl.close_dialog();
					this.appl.notify("password changed");
				}
			},this);		
		};
		
		Dialog.prototype.cancel = function(){
			this.appl.close_dialog();
		};
		
		return {
			viewModel: Dialog,
			template: main_tmpl
		};
	
	}
);