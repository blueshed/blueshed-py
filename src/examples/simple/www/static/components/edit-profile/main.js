define(["knockout",
        "text!./main-tmpl.html",
        "blueshed/utils/random-str",
        "blueshed/bindings/ko-dropzone"],
	function(ko, main_tmpl, randomStr){
	
		function Dialog(params){
			this.appl = params.appl;
			this.id = ko.observable(ko.unwrap(params.user.id));
			this.email = ko.observable(ko.unwrap(params.user.email)).extend({required:true});
			this.firstname = ko.observable(ko.unwrap(params.user.firstname)).extend({required:true});
			this.lastname = ko.observable(ko.unwrap(params.user.lastname)).extend({required:true});
			this.photo = ko.observable(ko.unwrap(params.user.photo));
			this.permissions = ko.observableArray(ko.unwrap(params.user.permissions));
			this.all_permissions = appl.store.permissions();
			
			this.error = ko.observable();
			
			this.isValid = ko.validatedObservable({
				email: this.email,
				firstname: this.firstname,
				lastname: this.lastname,
				photo: this.photo
			});	
			
            this.photo_args = ko.computed(function(){
            	var args = {
            		url: "/images/",
            		maxFiles:1,
            		createImageThumbnails: true,
    				success: function(file,response){
    					this.photo(response.result.file.thumb);
    				}.bind(this),
    				sending: function(file, xhr, formData) {
    					formData.append("prefix", 'person/'+ randomStr(8));
    				}.bind(this),
    				complete:function(file){
    					this.removeFile(file);
    				},
    				dictDefaultMessage:"Drop file here or 'click' to choose"
            	};
            	return args;
            },this);
		}
		
		Dialog.prototype.submit = function(){
			this.appl.connection.send({
				action:'save_person',
				args: {
					id: this.id(),
					values: ko.toJS({
						email: this.email,
						firstname: this.firstname,
						lastname: this.lastname,
						photo: this.photo,
						permissions_: this.permissions
					})
				}
			}, 
			function(response){
				if(response.error){
					this.error(response.error);
				} else {
					this.appl.close_dialog();
					this.appl.notify("profile saved");
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