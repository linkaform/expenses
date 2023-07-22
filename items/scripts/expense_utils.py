# -*- coding: utf-8 -*-
import sys, simplejson
from linkaform_api import settings, network, utils, lkf_models
from account_settings import *
from datetime import datetime, timedelta
from pytz import timezone


def unlist(arg):
    if type(arg) == list and len(arg) > 0:
        return unlist(arg[0])
    return arg


class Expenses():

    def __init__(self, cr, lkf_api, settings):
        self.lkf_api = lkf_api
        lkm = lkf_models.LKFModules(settings)
        print('lkf moudles', lkm.catalog_id('solicitudes_de_gastos'))
        self.CATALOG_SOL_VIAJE = lkm.catalog_id('solicitudes_de_gastos')
        self.CATALOG_SOL_VIAJE_ID = self.CATALOG_SOL_VIAJE.get('id')
        self.CATALOG_SOL_VIAJE_OBJ_ID = self.CATALOG_SOL_VIAJE.get('obj_id')

        self.CATALOG_RESP_AUT = lkm.catalog_id('responsables_de_autorizar_gastos')
        self.CATALOG_RESP_AUT_ID = self.CATALOG_RESP_AUT.get('id')
        self.CATALOG_RESP_AUT_OBJ_ID = self.CATALOG_RESP_AUT.get('obj_id')
        
        self.CATALOG_EMPLEADOS = lkm.catalog_id('catalogo_de_empleados')
        self.CATALOG_EMPLEADOS_ID = self.CATALOG_EMPLEADOS.get('id')
        self.CATALOG_EMPLEADOS_OBJ_ID = self.CATALOG_EMPLEADOS.get('obj_id')
        
        self.CATALOG_MONEDA = lkm.catalog_id('moneda')
        self.CATALOG_MONEDA_ID = self.CATALOG_MONEDA.get('id')
        self.CATALOG_MONEDA_OBJ_ID = self.CATALOG_MONEDA.get('obj_id') 

        self.CATALOG_CONCEPTO_GASTO = lkm.catalog_id('conceptos_de_gastos')
        self.CATALOG_CONCEPTO_GASTO_ID = self.CATALOG_CONCEPTO_GASTO.get('id')
        self.CATALOG_CONCEPTO_GASTO_OBJ_ID = self.CATALOG_CONCEPTO_GASTO.get('obj_id')
        
        self.FORM_ID_SOLICITUD = lkm.form_id('solicitud_de_viticos','id')
        self.FORM_ID_AUTORIZACIONES = lkm.form_id('autorizacin_de_viaticos','id')
        self.FORM_ID_GASTOS_VIAJE = lkm.form_id('registros_de_gastos_de_viaje','id')
        self.FORM_ID_ENTREGA_EFECTIVO = lkm.form_id('entrega_de_anticipo','id')
        self.FORM_ID_GASTOS = lkm.form_id('registros_de_gastos_de_viaje','id') #CAMBIAR POR SOLO GASTOS
        self.FORM_SOLICITUD_VIATICOS_ID = lkm.form_id('solicitud_de_viticos','id') 
        self.SOL_RECORD = None
        self.SOL_DATA = None
        if cr:
            self.cr = cr

    def get_solicitud(self, folio):
        records = self.cr.find({
            'form_id':  self.FORM_ID_SOLICITUD,
            'deleted_at': {'$exists': False},
            'folio':folio
            }, 
            )
        rec = [ r for r in records]
        self.SOL_RECORD = unlist(rec)
        return self.SOL_RECORD

    def set_solicitud_catalog(self, folio, destino_de_viaje=None):
        # info_catalog = current_record['answers'].get(self.CATALOG_SOL_VIAJE_OBJ_ID, {})
        # destino_de_viaje = info_catalog.get('610419b5d28657c73e36fcd4', '')
        # print('info_catalog', info_catalog)
        # folio = info_catalog.get('610419b5d28657c73e36fcd3', '')
        mango_query = {"selector":
            {"answers":
                {"$and":[
                    {'610419b5d28657c73e36fcd3': {'$eq': folio}}
            ]}},
        "limit":1,
        "skip":0}
        if destino_de_viaje:
            mango_query['selector']['answers']['$and'].append({'610419b5d28657c73e36fcd4': {'$eq': destino_de_viaje}})
        res = self.lkf_api.search_catalog( self.CATALOG_SOL_VIAJE_ID, mango_query, jwt_settings_key='USER_JWT_PARENT')
        print('destino', destino_de_viaje)
        print('mango_query',mango_query)
        print(' --- CATALOG_SOL_VIAJE_ID =',self.CATALOG_SOL_VIAJE_ID)
        if res and len(res) > 0:
            self.SOL_DATA = res[0]
        else:
            
            #raise(simplejson.dumps({"error":f"No encontro alguna solucitid con el folio: {folio} y destino: {destino_de_viaje}"}))

            msg_error_app = {
                "610419b5d28657c73e36fcd4":{
                    "msg": [f"No encontro alguna solucitid con el folio: {folio} y destino: {destino_de_viaje}"],
                    "label": "Destino de viaje",
                    "error":[]
                }
            }
            raise Exception(simplejson.dumps(msg_error_app))

        return True

    def get_autorizador(self, folio_solicitud=None):
        if self.SOL_RECORD:
            record = self.SOL_RECORD.get('answers',{}).get(self.CATALOG_RESP_AUT_OBJ_ID)
        elif record:
            record = self.get_solicitud(folio_solicitud)
        auth_catalog = record.get('answers',{}).get(self.CATALOG_RESP_AUT_OBJ_ID)
        return auth_catalog

    def validar_fecha_vencida(self, fecha_gasto):
        date_fecha_gasto = datetime.strptime(fecha_gasto, '%Y-%m-%d')
        fecha_actual = datetime.now()
        diff_dates = fecha_actual - date_fecha_gasto
        return diff_dates.days > 15

    def update_solicitud_nested_catalog_values(self, data):

        data.update({
            # self.CATALOG_MONEDA_OBJ_ID:{'62aa1fa92c20405af671d123':self.SOL_DATA.get('62aa1fa92c20405af671d123')},
            # self.CATALOG_EMPLEADOS_OBJ_ID:{
                '6092c0ebd8b748522446af26':self.SOL_DATA.get('6092c0ebd8b748522446af26'),
                '6092c0ebd8b748522446af27':[unlist(self.SOL_DATA.get('6092c0ebd8b748522446af27',[])),],
                '6092c0ebd8b748522446af28':[unlist(self.SOL_DATA.get('6092c0ebd8b748522446af28',[])),],
                # }
            })
        return data

    def update_expense_catralog_values(self, current_record, total_gasto, anticipo_efectivo=None):
        folio = self.SOL_DATA.get('610419b5d28657c73e36fcd3')
        if current_record.get('form_id') == self.FORM_ID_GASTOS:
            folio_gasto = current_record.get('folio')
        else:
            folio_gasto = None
        monto_aprobado = self.SOL_DATA.get('610419e33a05c520d90814d3', 0)
        # gasto_ejecutado = self.SOL_DATA.get('629fb33a8758b5808890b22e', 0)
        monto_restante = self.SOL_DATA.get('629fb33a8758b5808890b22f', 0)
        current_status = self.SOL_DATA.get('610419b5d28657c73e36fcd7', '')
        fecha_fin = self.SOL_DATA.get('610419b5d28657c73e36fcd6', '')
        gasto_ejecutado  = self.get_all_related_expenses(folio, total_gasto, folio_gasto)
        if not monto_restante:
            monto_restante = monto_aprobado
        monto_restante = round(monto_aprobado - gasto_ejecutado,2)
        info_to_set = {
            '629fb33a8758b5808890b22e': gasto_ejecutado, 
            '629fb33a8758b5808890b22f': monto_restante,
            }
        if anticipo_efectivo:
            info_to_set.update({'649d02057880ff495300bcc0':anticipo_efectivo})
        else:
            anticipo_efectivo = self.SOL_DATA.get('649d02057880ff495300bcc0', 0)
        ###
        #TODO CALCULAR EL MONTO DE EFECTIVO RESTANTE... 649d02057880ff495300bcc1
        ####
        ####
        ####
        payment_method = current_record.get('answers',{}).get('5893798cb43fdd4b53ab6e1e','').lower()
        if not 'debito' in payment_method or not 'efectivo' in payment_method:
            total_gasto = 0
        monto_efectivo_gastado = self.get_all_related_expenses(folio, total_gasto, folio_gasto, cash_only=True)
        monto_efectivo_restante = anticipo_efectivo - monto_efectivo_gastado
        info_to_set.update({'649d02057880ff495300bcc1': monto_efectivo_restante, '649d02057880ff495311bcc0':monto_efectivo_gastado})
        info_to_set = self.update_solicitud_nested_catalog_values(info_to_set)
        if current_status == 'Abierto' and self.validar_fecha_vencida( fecha_fin ):
            print('revisar este caso... si ya pasaron mas de 15 dias no debe de dejar guardar....')
            autorizacion_viaticos(folio)
            #crear autorizacion de viaticos
            info_to_set.update({'610419b5d28657c73e36fcd7': 'Vencido'})
        elif monto_restante < 0:
            # autorizacion_viaticos(folio)
            #crear autorizacion de viaticos
            info_to_set.update({
                '610419b5d28657c73e36fcd7': 'Sobregirado'
            })
        elif monto_restante == 0:
            # autorizacion_viaticos(folio)
            #crear autorizacion de viaticos
            info_to_set.update({
                '610419b5d28657c73e36fcd7': 'Cerrado'
            })

        res_update = self.lkf_api.update_catalog_multi_record(info_to_set, self.CATALOG_SOL_VIAJE_ID, record_id=[ self.SOL_DATA[ '_id' ], ], jwt_settings_key='USER_JWT_PARENT')
        update_ok = False
        if isinstance(res_update, dict):
            if res_update.get('status_code',0) == 202:
                update_ok = True
        elif isinstance(res_update, list) and len(res_update) > 0 :
            update_ok = True

        if update_ok:
            group_gastos = self.get_all_related_expenses_rec(folio, current_record)
            update_db = self.cr.update_one({
                'folio': folio,
                'form_id': self.FORM_SOLICITUD_VIATICOS_ID,
                'deleted_at': {'$exists': False}
            },{'$set':{
                f'answers.{self.CATALOG_SOL_VIAJE_OBJ_ID}': {
                    '610419b5d28657c73e36fcd3': folio,
                    '610419b5d28657c73e36fcd4': [ self.SOL_DATA.get('610419b5d28657c73e36fcd4') ],
                    '610419e33a05c520d90814d3': [ self.SOL_DATA.get('610419e33a05c520d90814d3') ],
                    '629fb33a8758b5808890b22e': [ gasto_ejecutado ],
                    '649d02057880ff495300bcc1': [ monto_efectivo_restante ],
                    '629fb33a8758b5808890b22f': [ monto_restante ],
                    '610419b5d28657c73e36fcd7': [ info_to_set.get('610419b5d28657c73e36fcd7', current_status) ]
                },
                'answers.62aa1ed283d55ab39a49bd2d':group_gastos
                }
            })
            db_res = update_db.raw_result
            print('raw_result',db_res)
        return update_ok

    def get_all_related_expenses_rec(self, folio_sol, current_record={}):
        match_query  = {
                    'form_id': {'$in': [self.FORM_ID_GASTOS_VIAJE, self.FORM_ID_ENTREGA_EFECTIVO]},
                    'deleted_at': {'$exists': False},
                    f'answers.{self.CATALOG_SOL_VIAJE_OBJ_ID}.610419b5d28657c73e36fcd3':folio_sol,
                }
                
        records = self.cr.find(match_query,{'answers':1, 'folio':1})
        records = self.cr.aggregate([
            {'$match': match_query },
            {"$project":{
                    "_id":0,
                    "62aa1fa92c20405af671d120":"$folio", #folio
                    "583d8e10b43fdd6a4887f55b":"$answers.583d8e10b43fdd6a4887f55b", #fecha
                    "aaaa1fa92c20405af671d123":f"$answers.{self.CATALOG_MONEDA_OBJ_ID}.62aa1fa92c20405af671d123", #Moneda
                    "aaaa1fa92c20405af671d122":"$answers.544d5ad901a4de205f3934ed", #Monteo en Moneda Extranjera
                    #"62aa1fa92c20405af671d122":"$answers.544d5ad901a4de205f391111", #Monto
                    "62aa1fa92c20405af671d122":{"$cond" :[
                        {"$eq":["$form_id",self.FORM_ID_ENTREGA_EFECTIVO]},
                        {'$multiply': ["$answers.544d5ad901a4de205f391111",-1]},
                        "$answers.544d5ad901a4de205f391111"]}, #Monto
                    "627bf0d5c651931d3c7eedd3":"$answers.627bf0d5c651931d3c7eedd3", #Monto Autorizado
                    f"{self.CATALOG_CONCEPTO_GASTO_OBJ_ID}.649b2a84dac4914e02aadb24":f"$answers.{self.CATALOG_CONCEPTO_GASTO_OBJ_ID}.649b2a84dac4914e02aadb24", #Concepto
                    "62aa1fa92c20405af671d124":"$answers.544d5b4e01a4de205e2b2169", #Estatus
                    "5893798cb43fdd4b53ab6e1e":"$answers.5893798cb43fdd4b53ab6e1e", #Metodo de Pgo
                }
            },
            {"$sort":{"583d8e10b43fdd6a4887f55b":1}}
            ])
        res  = []
        #TODO SI NO EXISTE EL REGISTRO OSEA ES UNO NUEVO HAY QUE AGREGAR EL SET DEL CURREN RECORD
        this_set = {}
        if current_record and not current_record.get('folio'):
            answers = current_record.get('answers')
            this_set ={
                    "62aa1fa92c20405af671d120":"Pending", #folio
                    "583d8e10b43fdd6a4887f55b":answers.get("583d8e10b43fdd6a4887f55b"), #fecha
                    "aaaa1fa92c20405af671d123":answers.get(self.CATALOG_MONEDA_OBJ_ID,{}).get("62aa1fa92c20405af671d123"), #Moneda
                    "aaaa1fa92c20405af671d122":answers.get("544d5ad901a4de205f3934ed"), #Monteo en Moneda Extranjera
                    "62aa1fa92c20405af671d122":answers.get("544d5ad901a4de205f391111"), #Monto
                    "627bf0d5c651931d3c7eedd3":answers.get("627bf0d5c651931d3c7eedd3"), #Monto Autorizado
                    self.CATALOG_CONCEPTO_GASTO_OBJ_ID:{self.CATALOG_CONCEPTO_GASTO_OBJ_ID:answers.get(self.CATALOG_CONCEPTO_GASTO_OBJ_ID,{}).get("649b2a84dac4914e02aadb24")}, #Concepto
                    "62aa1fa92c20405af671d124":answers.get("544d5b4e01a4de205e2b2169"), #Estatus
            }
        for r in records:
            res.append(r)
        if this_set:
            res.append(this_set)
        return res

    def get_all_related_expenses(self, folio_sol, this_expense, folio_rec, status=None, cash_only=False):
        #TODO QUERY ALL EXPENSES
        if not status:
            status = ['por_autorizar', 'en_progreso', 'autorizado']
        elif isinstance(status, str):
            status = [status, ]
        match_query  = {
                    'form_id': self.FORM_ID_GASTOS_VIAJE,
                    'deleted_at': {'$exists': False},
                    f'answers.{self.CATALOG_SOL_VIAJE_OBJ_ID}.610419b5d28657c73e36fcd3':folio_sol,
                    'answers.544d5b4e01a4de205e2b2169': {'$in':status},

                }
        if folio_rec:
            #excluir el gasto de este registro del quiery el gasto de este registro
            match_query.update({'folio':{'$ne':folio_rec}})
        if cash_only:
            match_query.update( {"$or":[
                # {f'answers.5893798cb43fdd4b53ab6e1e':'Efectivo - Debito'},
                {f'answers.5893798cb43fdd4b53ab6e1e':{ '$regex': 'efectivo', '$options': 'i',}},
                {f'answers.5893798cb43fdd4b53ab6e1e':{ '$regex': 'debito',   '$options': 'i',}},
                # {f'answers.5893798cb43fdd4b53ab6e1e':'Efectivo - Debito'},
                ]})
        records = self.cr.aggregate([
            {'$match': match_query },
            {'$project':{
                '_id':1,
                'total_gasto': '$answers.544d5ad901a4de205f391111',
                'total_autorizado':{'$ifNull':['$answers.627bf0d5c651931d3c7eedd3','$answers.544d5ad901a4de205f391111']},
                'solicitud':f'$answers.{self.CATALOG_SOL_VIAJE_OBJ_ID}.610419b5d28657c73e36fcd3',
            }},
            {'$project':{
                '_id':1,
                'solicitud':'$solicitud',
                'total_gasto': "$total_autorizado",
            }},
            {'$group':{
                '_id':{
                    'solicitud':'$solicitud'
                },
                'total':{'$sum':'$total_gasto'}
            }}
            ])
        total = this_expense
        for r in records:
            total += r.get('total')
        return total

    def autorizacion_viaticos(self, folio, destino=None):
        self.set_solicitud_catalog(folio, destino)
        self.get_solicitud(folio)
        autorizador = self.get_autorizador()
        n = datetime.now( tz=timezone('America/Monterrey') )
        from_date = n - timedelta(days=7)
        records_to_process = self.get_all_related_expenses_rec(folio)
        # Autorización de Viáticos / 94192
        metadata = self.lkf_api.get_metadata(self.FORM_ID_AUTORIZACIONES)
        list_to_group = []
        new_record = self.SOL_RECORD.get('answers')
        new_record.update({
            '610419e33a05c520d90814d3':self.SOL_DATA.get('610419e33a05c520d90814d3'),
            '649d02057880ff495300bcc0':self.SOL_DATA.get('649d02057880ff495300bcc0'),
            '629fb33a8758b5808890b22e':self.SOL_DATA.get('629fb33a8758b5808890b22e'),
            '649d02057880ff495311bcc0':self.SOL_DATA.get('649d02057880ff495311bcc0'),
            '649d02057880ff495300bcc1':self.SOL_DATA.get('649d02057880ff495300bcc1'),
            '629fb33a8758b5808890b22f':self.SOL_DATA.get('629fb33a8758b5808890b22f'),
            '62954ccb8e54c96dc34995a5': 'pendiente_por_autorizar',
            })
        if self.SOL_RECORD['form_id'] == self.FORM_ID_SOLICITUD:
            new_record.update({"649b512cbf4cc1fab1133b7a":"viatico"})
        for record in records_to_process:
            info_to_set = record
            # info_to_set.update({
            #     '62aa1fa92c20405af671d120': record.get('folio'), #folio
            # })
            list_to_group.append(info_to_set)
        new_record['62aa1ed283d55ab39a49bd2d'] = list_to_group
            # Preparo el registro a crear en la forma Autorización de Viáticos
        metadata.update({
            'properties': {
                "device_properties":{
                    "system": "Script",
                    "process": "Autorización de Viáticos",
                    "accion": 'Crear registro de Autorización',
                    "folio solicitud": folio,
                    "archive": "solicitar_autorizacion.py"
                }
            },
            "answers":new_record,
            "folio":folio + '1'
        })
        print('metadata=',metadata)
        res_create = self.lkf_api.post_forms_answers(metadata)
        print('res_create=',res_create)
        # if res_create.get('status_code', 0) == 201:
        #     # Actualizar el estatus de los folios incluidos en la Autorizació a "En Proceso"
        #     for form_id in dict_records:
        #         list_folios = dict_records[form_id]
        #         if form_id == FORM_ID_GASOTS_VIAJE:
        #             res_update = lkf_api.patch_multi_record({'544d5b4e01a4de205e2b2169': 'en_proceso'}, form_id, folios=list_folios, jwt_settings_key='JWT_KEY', threading=True)
        #             print('form_id= {} res_update= {}'.format(form_id, res_update))
        #         else:
        #             for folio in list_folios:
        #                 record_to_update = dict_all_info_records[folio]
        #                 print('before update folio= {} _id={}'.format(folio, record_to_update.get('_id')))
        #                 if record_to_update.get('_id'):
        #                     res_update = lkf_api.patch_record(record_to_update, jwt_settings_key='JWT_KEY')
        #                     print('folio= {} res_update= {}'.format(folio, res_update))
        #     # Se debe pegar el nombre de quien creo el registro Delivery o Solicitud en el created_by_name
        #     folio_created = res_create.get('json',{}).get('folio','')
        #     res_update_record_created = cr.update_one({
        #         'form_id': FORM_ID_AUTORIZACIONES,
        #         'deleted_at': {'$exists': False},
        #         'folio': folio_created
        #     }, {'$set': {'created_by_name': name_user}})
        #     print('res_update_record_created=',res_update_record_created)