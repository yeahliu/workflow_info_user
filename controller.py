# -*- coding: utf-8 -*-
##############################################################################
#
#    yeahliu
#    Copyright (C) yeahliu (<talent_qiao@163.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.pooler as pooler

import time
import openerp
import openerp.modules.registry
from openerp.tools.translate import _
from openerp.tools import config
from openerp import SUPERUSER_ID
import web.http as openerpweb
import openerp.addons.web.controllers.main as cmain
import openerp.netsvc as netsvc
import openerp.addons.web.controllers.main as oeweb


#----------------------------------------------------------
# OpenERP Web helpers
#----------------------------------------------------------

class WklDataset(cmain.DataSet):
    
    
    def check_workflow_user(self,req,model,res_id,signal):
        cr = pooler.get_db(req.session._db).cursor()
        uid = req.session._uid
        
        """如果是管理员，则直接返回"""
        if uid == SUPERUSER_ID:
            cr.close()
            return True 
        
        try:
            """ 如果group_id和user_field都为空，则无权限控制 """
            cr.execute("""
                select 1 from wkf_transition wtr left join wkf_activity wac on wtr.act_from=wac.id 
                    left join wkf_workitem wim on wim.act_id=wac.id 
                    left join wkf_instance wis on wim.inst_id=wis.id 
                where wis.res_id=%s and wis.res_type=%s and wis.state='active' 
                    and wtr.signal=%s and wtr.group_id is null and wtr.user_field is null """,(res_id,model,signal))
            res_cr = bool(cr.fetchone())
            if res_cr :
                return True
            
            """ 检查user_field """
            cr.execute("""
                select wtr.user_field from wkf_transition wtr left join wkf_activity wac on wtr.act_from=wac.id 
                    left join wkf_workitem wim on wim.act_id=wac.id 
                    left join wkf_instance wis on wim.inst_id=wis.id 
                where wis.res_id=%s and wis.res_type=%s and wis.state='active'  
                    and wtr.signal=%s and wtr.user_field is not null """,(res_id,model,signal))
            r = cr.fetchone()
            if  r :
                (user_field,) = r
                fields= {}
                context = {}
                obj = pooler.get_pool(req.session._db).get(model).browse(cr,uid,res_id)
                obj_user_id = obj[user_field]
                # 如果设置了指定人，则必须为当前用户
                if obj_user_id and obj_user_id.id== uid :
                    return True
                else :
                    return False 
            
            """检查 group"""
            cr.execute("""
                select wtr.group_id from wkf_transition wtr left join wkf_activity wac on wtr.act_from=wac.id 
                    left join wkf_workitem wim on wim.act_id=wac.id 
                    left join wkf_instance wis on wim.inst_id=wis.id 
                    left join res_groups_users_rel ug_rel on ug_rel.gid=wtr.group_id 
                    left join res_users u on u.id=ug_rel.uid
                where wis.res_id=%s and wis.res_type=%s and wis.state='active'  
                    and wtr.signal=%s and group_id is not null 
                """ ,(res_id,model,signal))
            r  = cr.fetchone()
            if  r :
                (group_id,) = r
                user_groups = pooler.get_pool(req.session._db).get('res.users').read(cr, uid, [uid], ['groups_id'])[0]['groups_id']
                if group_id in user_groups:
                    return True 
        except Exception:
            cr.rollback()
            raise
        finally:
            cr.close()
        return False
    
    @openerpweb.jsonrequest
    def workflow_can_pro(self,req,model,id,signal):
        can_pro = self.check_workflow_user(req, model, id, signal)
        if not can_pro :
            return {"result":False,"signal":signal}
        return {"result":True,"signal":signal} ;
    
    @openerpweb.jsonrequest
    def exec_workflow(self, req, model, id, signal):
        addons = oeweb.module_boot(req, req.session._db)
        if addons :
            if 'workflow_info_user' in addons :
                can_pro = self.check_workflow_user(req, model, id, signal)
                if not can_pro:
                    return {} 
        
        return req.session.exec_workflow(model, id, signal)
    


# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
