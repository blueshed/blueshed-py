define(
	["knockout",
	 "knockout-mapping",
	 "./note-item"],
	function(ko,mapping,NoteItem){
		
		function Note(options){
			this._type = "Note"
			this.id = ko.observable();
			this.title = ko.observable();
			this.tags = ko.observableArray();
			this.items = ko.observableArray();
			if(options){
				this.update(options);
			}
		}
		
		
		Note.prototype.update = function(options){
			
			// remove items without ids
			this.items().filter(function(item){
				return item.id();
			}).map(function(item){
				this.item.remove(item);
			}.bind(this));
			
			mapping.fromJS(options,{
				items:{
					key: function(item){
						return ko.unwrap(item.id);
					},
					create: function(options){
						return new NoteItem(options.data);
					}
				},
				include:["id","title","tags","items"]
			},this);
		};
		
		
		Note.prototype.save = function(){
			return mapping.toJS(this,{});
		};
		

		Note.prototype.add_item = function(options){
			var result = new NoteItem(options);
			this.items.push(result);
			return result;
		};

		
		return Note;
	}
);