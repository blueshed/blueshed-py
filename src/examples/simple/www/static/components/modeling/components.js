define([
        "knockout",
		"./view/mysql",
		"./view/sqlite",
		"./view/sqlalchemy",
	    "text!./model-list-tmpl.html",
	    "text!./model-editor-tmpl.html",
	    "text!./schema/data-table-tmpl.html"
        ],
        function(ko,
        		MySQL,
        		SQLite,
        		SQLAlchemy,
        		model_list_tmpl, 
			 	model_editor_tmpl,
			 	data_table_tmpl){


	ko.components.register("mysql-script",MySQL);
	ko.components.register("sqlite-script",SQLite);
	ko.components.register("sa-script",SQLAlchemy);
	
	ko.components.register("model-list",{
        template: model_list_tmpl
    });

    ko.components.register("model-editor",{
        template: model_editor_tmpl
    });

    ko.components.register("data-table",{
        template: data_table_tmpl
    });
    
});