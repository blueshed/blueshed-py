define([
		"knockout",
		"text!./main-tmpl.html"
	],
	function(ko, main_tmpl){

		function Panel(params){
			this.appl = params.appl;
			this.title = params.title;
			this.status = this.appl.connection.status;
		}

		Panel.prototype.init = function() {
			// nasty hack to do things you can't with knockout
			// like using jquery - yuk.
		};

		Panel.prototype.dispose = function() {
			// called when torn down.
		};

		return {
			template: main_tmpl,
			viewModel: Panel
		};
	}
);