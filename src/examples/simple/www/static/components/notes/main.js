define(
	["jquery",
	 "knockout",
	 "text!./main.html",
	 "./note",
	 "blueshed/dialog",
	 "blueshed/notify",
	 "./ko-note-map",
	 "blueshed/bindings/ko-enter",
	 "gridster"],
	function($,ko,tmpl_html,Note,Dialog,Notify,NoteMaps){
		
		function GridsterPanel(params){
			window.gpanel = this;
			this.appl = params.appl;
			this.args = params.args || [];
			this.code_address = ko.observable();
			this.loaded = NoteMaps;

			this.notes = ko.observableArray();
			this.selected_note = ko.observableArray();
			this.selected_widget = ko.observable();
			this.sub = this.appl.connection.broadcast.subscribe(function(message){
				var note = null;
				if(message.signal == "saved_note"){
					note = this.get_note_by_id(message.message.id);
					if(note){
						note.update(message.message);
						Notify.notify("updated");
					}
				}
				else if(message.signal == "removed_note"){
					note = this.get_note_by_id(message.message.id);
					if(note){
						if(this.selected_note() == note){
							this.selected_item(null);
							this.selected_note(null);	
						}
						this.notes.remove(note);
						Notify.notify("removed");
					}
				}
			},this);
		}

		GridsterPanel.prototype.init = function() {
			this.show.apply(this,this.args);
		};
		
		GridsterPanel.prototype.dispose = function() {
			window.gpanel = null;
			this.sub.dispose();
			this.sub = null;
			this.gridster.destroy();
		};

		GridsterPanel.prototype.save = function(){
			var item = this.selected_note();
			var value = item.save();
			this.appl.connection.rpc("save_note",value,function(response){
            	if(response.error){
            		Notify.error(response.error);
            		return;
            	}
				item.id(response.result);
        		Notify.notify("saved");
			}.bind(this));
		};
		
		GridsterPanel.prototype.show = function(id) {
			if(id){
				this.load_id(id);
			} else {
				this.selected_note(new Note());
				this.add_widget({type:'note',text:'Hello, World!'});
				this.add_widget({type:'image',image:'//blueshed-notes.s3.amazonaws.com/thumbnail.jpg'});
				this.add_widget({type:'map',
								 lat: 54.81433415399176,
								 lng: 357.0305852355957,
								 zoom: 6});
			}
		};
		
		GridsterPanel.prototype.load_id = function(id){
			if(id){
				this.appl.connection.rpc("get_notes",{
					id: id
				}, function(response){
	            	if(response.error){
	            		Notify.error(response.error);
	            		return;
	            	}
	            	var note = new Note(response.result);
					this.selected_note(note);
				}.bind(this));
			}
		};
		
		GridsterPanel.prototype.get_note_by_id = function(id){
			return this.notes().find(function(item){
				return ko.unwrap(item.id) == id;
			},this);
		};
		
		
		GridsterPanel.prototype.init_grid = function(){
			 this.gridster = $(".gridster ul").gridster({
                widget_margins: [10, 10],
                widget_base_dimensions: [140, 140],
                avoid_overlapped_widgets: true,
                resize: {
                    enabled: true,
                    stop: this.update_widget.bind(this)
                },
                draggable:{
               	 stop: this.update_widget.bind(this)
                }
			 }).data('gridster');
		};
		

		GridsterPanel.prototype.added_widget = function(node, index, obj) {
			if(node.nodeName == "LI"){
				var $node = $(node);
				this.gridster.add_widget($node, obj.width(), obj.height());
	            obj.col(parseInt($node.attr("data-col")));
	            obj.row(parseInt($node.attr("data-row")));
	            obj.width(parseInt($node.attr("data-sizex")));
	            obj.height(parseInt($node.attr("data-sizey")));
			}
		};
		

		GridsterPanel.prototype.removed_widget = function(node, index, obj) {};
	
		
		GridsterPanel.prototype.add_widget = function(options){
			this.selected_widget(this.selected_note().add_item(options));
		};
		
		GridsterPanel.prototype.update_widget = function(){
			this.selected_note().items().map(function(obj){
				var widget = $("#" + obj.id());
		        var column = widget.attr("data-col");
		        if (column) {
		        	obj.col(parseInt(column));
		            obj.row(parseInt(widget.attr("data-row")));
		            obj.width(parseInt(widget.attr("data-sizex")));
		            obj.height(parseInt(widget.attr("data-sizey")));
		        }
			});
			$(".map").trigger('wd-resize');
		};

		GridsterPanel.prototype.edit_widget = function(item){
			this.selected_widget(item);
		};

		GridsterPanel.prototype.remove_widget = function(){
			var item = this.selected_widget();
			var widget = $("#" + item.id());
			Dialog.open_dialog("blue-confirm-dialog",{
				title: "Remove Widget...",
				text: "Are you sure you want to delete this widget?",
				action: function(){
					this.selected_note().items.remove(item);
					this.gridster.remove_widget(widget);
					this.selected_widget(null);
					Dialog.close_dialog();
				}.bind(this),
				action_label: 'Remove',
				can_cancel: true
			});
		};

		GridsterPanel.prototype.image_change = function(data, response) {
            if(response.error){
            	this.error(response.error);
            } else {
                data(response.result['image[0]'].name);
                if(this.table){
                	this.table.render();
                }
            }
		};
		
		return {
			viewModel: GridsterPanel, 
			template: tmpl_html
		};
	}
);