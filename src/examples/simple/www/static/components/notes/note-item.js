define(
	["knockout",
	 "knockout-mapping"],
	function(ko,mapping){
		
		var id_seed = 1;
		
		function Widget(options){
			this._type = "NoteItem"
			this.id = ko.observable(id_seed++);
			this.row = ko.observable(1);
			this.col = ko.observable(1);
			this.width = ko.observable();
			this.height = ko.observable();

			this.type = ko.observable(this.types[0]);
			
			this.text = ko.observable();
			
			this.image = ko.observable();
			
			this.lat = ko.observable();
			this.lng = ko.observable();
			this.zoom = ko.observable();
			this.map_type = ko.observable();
			
			if(options){
				this.update(options);
			}
			
			this.dimensions = ko.pureComputed(function(){
				return [
				        "id:", this.id(),
				        " r:", this.row(),
				        " c:",this.col(),
				        " width:",this.width(),
				        " height:",this.height()].join("");
			},this,{deferEvaluation:true});
			this.location = ko.pureComputed(function(){
				return !isNaN(this.lat()) && !isNaN(this.lng());
			},this,{deferEvaluation:true});
		}
		
		Widget.prototype.types = ["note","image","map"];
		
		Widget.prototype.update = function(options){
			mapping.fromJS(options,{
				include:["id","row","col","width","height","text","image","lat","lng","zoom","map_type"],
				ignore:["types","dimensions"]
			},this);
		}

		return Widget;
	}
);