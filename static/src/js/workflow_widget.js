/*---------------------------------------------------------
 * workflow 增强
 * Copyright 2013 yeahliu <talent_qiao@163.com>
 *---------------------------------------------------------*/
openerp.workflow_info_user = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
	
    instance.web.form.WidgetButton.include({
    
    renderElement: function() {
        	this._super();
    		self = this ;
    		if( this.get("effective_invisible") == false){
	    		if( this.node.attrs.type == "workflow_ok" || this.node.attrs.type == "workflow_no"){
		    		this.$el.addClass(" "+this.node.attrs.name)
		    		var handle= function(result){
		    			if (result["result"] == false ){
		    				$("."+result["signal"]).hide() ;
		    			}
		    		}
	    			instance.session.rpc('/web/dataset/workflow_can_pro', {
											            model: self.getParent().model,
											            id: self.view.get_selected_ids()[0], // model ids
											            signal: this.node.attrs.name
											        }).then(handle);// then
					
	    		} // if
	    	}// if
	    } // start:function
	    
	}); // WidgetButton.include
}
// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
