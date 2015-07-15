define([
		"knockout",
		"text!./main-tmpl.html"
	],
	function(ko, main_tmpl){

		function Panel(params){
			this.appl = params.appl;
			this.items = ko.observableArray();
			this.selected = ko.observable();
		}

		Panel.prototype.init = function() {
			this.items([
				{id:"1",name:"foo"},
				{id:"2",name:"bar"}
			]);
		};

		Panel.prototype.dispose = function() {
			
		};

		return {
			template: main_tmpl,
			viewModel: Panel
		};
	}
);