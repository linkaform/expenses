# -*- coding: utf-8 -*-
import sys, simplejson
from linkaform_api import settings, network, utils, lkf_models
from account_settings import *
from datetime import datetime, timedelta, date
import time
from pytz import timezone


def unlist(arg):
    if type(arg) == list and len(arg) > 0:
        return unlist(arg[0])
    return arg

class Expenses():

    def __init__(self, settings, folio_solicitud=None):
        self.net = network.Network(settings)
        self.cr = self.net.get_collections()
        self.lkf_api = utils.Cache(settings)
        self.lkm = lkf_models.LKFModules(settings)
        config['PROTOCOL'] = 'https'
        config['HOST'] ='app.linkaform.com'
        settings.config.update(config)
        self.lkf_api_prod = utils.Cache(settings)
        


        self.CATALOG_SOL_VIAJE = self.lkm.catalog_id('solicitudes_de_gastos')
        self.CATALOG_SOL_VIAJE_ID = self.CATALOG_SOL_VIAJE.get('id')
        self.CATALOG_SOL_VIAJE_OBJ_ID = self.CATALOG_SOL_VIAJE.get('obj_id')

        self.CATALOG_RESP_AUT = self.lkm.catalog_id('responsables_de_autorizar_gastos')
        self.CATALOG_RESP_AUT_ID = self.CATALOG_RESP_AUT.get('id')
        self.CATALOG_RESP_AUT_OBJ_ID = self.CATALOG_RESP_AUT.get('obj_id')
        
        self.CATALOG_EMPLEADOS = self.lkm.catalog_id('catalogo_de_empleados')
        self.CATALOG_EMPLEADOS_ID = self.CATALOG_EMPLEADOS.get('id')
        self.CATALOG_EMPLEADOS_OBJ_ID = self.CATALOG_EMPLEADOS.get('obj_id')
        
        self.CATALOG_MONEDA = self.lkm.catalog_id('moneda')
        self.CATALOG_MONEDA_ID = self.CATALOG_MONEDA.get('id')
        self.CATALOG_MONEDA_OBJ_ID = self.CATALOG_MONEDA.get('obj_id') 

        self.CATALOG_CONCEPTO_GASTO = self.lkm.catalog_id('conceptos_de_gastos')
        self.CATALOG_CONCEPTO_GASTO_ID = self.CATALOG_CONCEPTO_GASTO.get('id')
        self.CATALOG_CONCEPTO_GASTO_OBJ_ID = self.CATALOG_CONCEPTO_GASTO.get('obj_id')
        
        self.FORM_ID_SOLICITUD = self.lkm.form_id('solicitud_de_viticos','id')
        self.FORM_ID_AUTORIZACIONES = self.lkm.form_id('autorizacin_de_viaticos','id')
        self.FORM_ID_GASTOS_VIAJE = self.lkm.form_id('registros_de_gastos_de_viaje','id')
        self.FORM_ID_ENTREGA_EFECTIVO = self.lkm.form_id('entrega_de_efectivo','id')
        self.FORM_ID_GASTOS = self.lkm.form_id('registros_de_gastos_de_viaje','id') #CAMBIAR POR SOLO GASTOS
        self.FORM_SOLICITUD_VIATICOS_ID = self.lkm.form_id('solicitud_de_viticos','id') 
        self.FORM_REGISTRO_DE_GASTOS_DE_VIAJE = self.lkm.form_id('registros_de_gastos_de_viaje')['id']

        self.SOL_RECORD = {}
        self.SOL_DATA = {}
        if folio_solicitud:
            self.SOL_DATA = self.set_solicitud_catalog(folio_solicitud)

    #Solicitud de Viaticos

    def get_cant_dias(self, answers):
        salida = answers.get('61041b50d9ee55ab14965ba2')
        regreso = answers.get('61041b50d9ee55ab14965ba3')
        salida_dt = datetime.strptime(salida, '%Y-%m-%d')
        regreso_dt = datetime.strptime(regreso, '%Y-%m-%d')
        cant_dias = regreso_dt - salida_dt
        return int(cant_dias.days)

    def update_solicitud_from_catalog(self, current_record ):
        folio = current_record['folio']
        mango_query = {"selector":
        {"answers":
            {"$and":[
                {'610419b5d28657c73e36fcd3': {'$eq': folio}}
        ]}},
        "limit":1,
        "skip":0}
        catalog_data = self.lkm.catalog_id('solicitudes_de_gastos')
        catalog_id = catalog_data.get('id')
        catalog_obj_id = catalog_data.get('obj_id')
        cant_dias = self.get_cant_dias(current_record['answers'])
        for x in range(3):
            res = self.lkf_api.search_catalog( self.lkm.catalog_id('solicitudes_de_gastos', 'id'), mango_query, jwt_settings_key='JWT_KEY')
            if not res:
                time.sleep(x)
        if not res:
            print('no se encontro el registro res=',mango_query)
            return False
        for r in res:
            set_answers = {
                catalog_obj_id:{
                    '610419b5d28657c73e36fcd3': folio,
                    '610419b5d28657c73e36fcd4': [ r.get('610419b5d28657c73e36fcd4') ],
                    '610419e33a05c520d90814d3': [ r.get('610419e33a05c520d90814d3') ],
                    '629fb33a8758b5808890b22e': [ r.get('629fb33a8758b5808890b22e') ],
                    '629fb33a8758b5808890b22f': [ r.get('629fb33a8758b5808890b22f') ],
                    '610419b5d28657c73e36fcd7': [ r.get('610419b5d28657c73e36fcd7') ],
                },
                '61041d15d9ee55ab14965bb5':cant_dias
            }
        print('set_answers', set_answers)
        res_update = self.lkf_api.patch_multi_record(
                    set_answers, current_record['form_id'], folios=[folio])

            # cr_res = self.cr.update_one({
            #     'folio': folio,
            #     'form_id': current_record['form_id'],
            #     'deleted_at': {'$exists': False}
            # },{'$set': {
            #     f'answers.{catalog_obj_id}': {
            #         '610419b5d28657c73e36fcd3': folio,
            #         '610419b5d28657c73e36fcd4': [ r.get('610419b5d28657c73e36fcd4') ],
            #         '610419e33a05c520d90814d3': [ r.get('610419e33a05c520d90814d3') ],
            #         '629fb33a8758b5808890b22e': [ r.get('629fb33a8758b5808890b22e') ],
            #         '629fb33a8758b5808890b22f': [ r.get('629fb33a8758b5808890b22f') ],
            #         '610419b5d28657c73e36fcd7': [ r.get('610419b5d28657c73e36fcd7') ],

            #     },
            #     'answers.61041d15d9ee55ab14965bb5':cant_dias
            # }})
        print('res_update', res_update)
        status_code = False
        for r in res_update.get('json',{}).get('objects',[]):
            this_rec = r.get(folio)
            status_code = this_rec.get('status_code')
            if status_code:
                break

        print('status_code', status_code)
        return status_code

    def validaciones_solicitud(self, answers):
        destino = answers.get('61041b50d9ee55ab14965000')
        dia_salida = answers.get('61041b50d9ee55ab14965ba2')
        dia_regreso = answers.get('61041b50d9ee55ab14965ba3')
        print('dia salida', dia_salida)
        print('dia_regreso', dia_regreso)
        msg_error_app = {}
        dia_salida_s = dia_salida.split('-')
        dia_regreso_s = dia_regreso.split('-')
        dia = date(int(dia_salida_s[0]),int(dia_salida_s[1]),int(dia_salida_s[2]))
        dia_r = date(int(dia_regreso_s[0]),int(dia_regreso_s[1]),int(dia_regreso_s[2]))
        cant_dias = (dia_r - dia).days
        print('cant_dias', cant_dias)
        answers['61041d15d9ee55ab14965bb5'] = cant_dias
        if cant_dias < 0:
            msg_error_app.update({
                    "61041b50d9ee55ab14965ba2":{
                        "msg": [f"La fecha de salida {dia_salida}, debe de ser mayor que la fecah de regreso{dia_regreso}."], 
                        "label": "Fecha de Salida", "error":[]},
                })
        if msg_error_app:
                raise Exception(simplejson.dumps(msg_error_app))
        return answers

    def get_total(self, answers):
        subtotal = answers.get('62914e2d855e9abc32eabc17', 0)
        impuesto = answers.get('62914e2d855e9abc32eabc18', 0)
        propina = answers.get('62914e2d855e9abc32eabc19', 0)
        expense_curreny = answers.get(self.CATALOG_MONEDA_OBJ_ID , {}).get('62aa1fa92c20405af671d123')
        print('2 CATALOG_SOL_VIAJE_OBJ_ID', self.CATALOG_SOL_VIAJE_OBJ_ID)
        info_catalog = answers.get(self.CATALOG_SOL_VIAJE_OBJ_ID, {})
        folio = info_catalog.get('610419b5d28657c73e36fcd3', '')
        destino = info_catalog.get('610419b5d28657c73e36fcd4', '')
        print('destino', destino)
        self.set_solicitud_catalog(folio, destino)
        print('solicitud', self.SOL_DATA)
        if not self.SOL_DATA:
            msg_error_app = {
                "6499b3586f2edb3da9155e3b":{"msg": [f"No se encontro en numero de solicitud {folio}, con destino: {destino} "], "label": "Numero de Solicitud", "error":[]},
            }
            raise Exception(simplejson.dumps(msg_error_app))
        currency = self.SOL_DATA.get('62aa1fa92c20405af671d123')
        print('currency=', currency)
        total_gasto = subtotal + impuesto + propina
        data = {
            "from":expense_curreny, 
            "date":answers.get('583d8e10b43fdd6a4887f55b'),
            "to":currency,
            "amount":total_gasto,
            "script_id":104621
            }
        amount_dict = self.lkf_api_prod.run_script(data)
        print('amount_dict', amount_dict)
        amount = amount_dict.get('json',{}).get('response',{}).get('amount')
        print('amount', amount)
        if not amount:
            if amount_dict.get('error'):
                raise Exception(simplejson.dumps(amount.get('error')))
            amount = total_gasto
        list_viaje_monto_restante = answers.get(self.CATALOG_SOL_VIAJE_OBJ_ID, {}).get('629fb33a8758b5808890b22f', ['0'])
        viaje_monto_restante = float( list_viaje_monto_restante[0] )
        #TODO REVISAR SI PERMITE SOBREGIRO
        # if total_gasto > viaje_monto_restante:
        #     msg_error_app = {
        #         "544d5ad901a4de205f3934ed":{"msg": [f"El Total del gasto ${total_gasto} no debe ser mayor al monto restante, {viaje_monto_restante}"], "label": "Subtotal", "error":[]},
        #     }
        #     raise Exception(simplejson.dumps(msg_error_app))
        answers['544d5ad901a4de205f3934ed'] = total_gasto
        answers['544d5ad901a4de205f391111'] = amount
        return answers

    def update_catalog(self, current_record):
        total_gasto = current_record['answers'].get('544d5ad901a4de205f391111', 0)
        print('total_gasto = ',total_gasto)
        total_gasto_aprobado = current_record['answers'].get('627bf0d5c651931d3c7eedd3')
        if total_gasto_aprobado == 0 or total_gasto_aprobado:
            total_gasto = total_gasto_aprobado
        print('total_gasto2 = ',total_gasto)
        print('total_gasto_aprobado = ',total_gasto_aprobado)
        return self.update_expense_catalog_values(current_record, total_gasto )

    def get_record_from_db(self, form_id, folio):
        query = {
            'form_id': form_id,
            'folio': folio,
            'deleted_at': {'$exists': False}
        }
        select_columns = {'folio':1,'user_id':1,'form_id':1,'answers':1}
        records = self.cr.find(query, select_columns)
        return [ x for x in records ] 

    def get_solicitud(self, folio):
        rec = self.get_record_from_db(self.FORM_ID_SOLICITUD, folio)
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
        res = self.lkf_api.search_catalog( self.CATALOG_SOL_VIAJE_ID, mango_query)
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

    def update_expense_catalog_values(self, current_record, total_gasto, anticipo_efectivo=None):
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
            self.autorizacion_viaticos(folio)
            #crear autorizacion de viaticos
            info_to_set.update({'610419b5d28657c73e36fcd7': 'Vencido'})
        elif monto_restante < 0:
            # autorizacion_viaticos(folio)
            #crear autorizacion de viaticos
            info_to_set.update({
                '610419b5d28657c73e36fcd7': 'Sobregirado'
            })
        elif monto_restante == 0:
            self.autorizacion_viaticos(folio)
            #crear autorizacion de viaticos
            info_to_set.update({
                '610419b5d28657c73e36fcd7': 'Cerrado'
            })

        res_update = self.lkf_api.update_catalog_multi_record(info_to_set, self.CATALOG_SOL_VIAJE_ID, record_id=[ self.SOL_DATA[ '_id' ], ])
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

    def get_all_related_expenses_rec(self, folio_sol=None, current_record={}):
        match_query  = {
            'form_id': {'$in': [self.FORM_ID_GASTOS_VIAJE, self.FORM_ID_ENTREGA_EFECTIVO]},
            'deleted_at': {'$exists': False},
            '$or':[{'answers.544d5b4e01a4de205e2b2169':'por_autorizar'}, {'answers.544d5b4e01a4de205e2b2169':'en_proceso'}]
            }
        if folio_sol:
            match_query.update({
                f'answers.{self.CATALOG_SOL_VIAJE_OBJ_ID}.610419b5d28657c73e36fcd3':folio_sol,
                })
                
        # records = self.cr.find(match_query,{'answers':1, 'folio':1})
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
            record['62aa1fa92c20405af671d124'] = 'autorizado'
            record['627bf0d5c651931d3c7eedd3'] = record.get('62aa1fa92c20405af671d122',)
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
            "folio":folio + '-1'
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

    def get_gasto_aprovado(self, dict_records_to_update, update=True):
        res = {}
        gasto_ejecutado_aprovado = 0
        gasto_ejecutado_efevo_aprovado = 0
        anticipo = 0
        form_id = self.FORM_REGISTRO_DE_GASTOS_DE_VIAJE
        for folio, gasto in dict_records_to_update.items():
            res[folio] = {}

            if gasto['status'] == 'no_autorizado':
                gasto['monto_autorizado'] = 0
            if gasto['status'] == 'autorizado':
                if 'efectivo' in gasto['metodo_pago'] or 'debito' in gasto['metodo_pago']:
                    if gasto['monto_autorizado'] > 0:
                        #si el monto es menor a 0 es un deposito
                        gasto_ejecutado_efevo_aprovado += gasto['monto_autorizado']
                        gasto_ejecutado_aprovado += gasto['monto_autorizado']
                    else:
                        #si el monto es menor a 0 es un deposito
                        anticipo += gasto['monto_autorizado']
                else:
                    gasto_ejecutado_aprovado += gasto['monto_autorizado']

            res[folio]['form_id'] = form_id
            if update:
                res_update = self.lkf_api.patch_multi_record(
                    {
                    '544d5b4e01a4de205e2b2169': gasto['status'],
                    '627bf0d5c651931d3c7eedd3': gasto['monto_autorizado'],#monto aturoizado
                    '6271bd58d96e7e7ab68d2c4b': gasto.get('motivo_no_autorizado'),#motivo
                    }, form_id, folios=[folio])
                res[folio]['status_code'] = res_update.get('status_code')
        res['gasto_ejecutado_aprovado'] = gasto_ejecutado_aprovado
        res['gasto_ejecutado_efevo_aprovado'] = gasto_ejecutado_efevo_aprovado
        res['anticipo'] = anticipo
        return res

    def update_autorization_records(self, answers):
        dict_records_to_update = {}
        form_id = self.FORM_REGISTRO_DE_GASTOS_DE_VIAJE
        # self.set_solicitud_catalog(folio)
        response = []
        for viatico in answers.get('62aa1ed283d55ab39a49bd2d', []):
            folio_origen = viatico.get('62aa1fa92c20405af671d120', '')
            dict_records_to_update[folio_origen] = dict_records_to_update.get(folio_origen,{})
            dict_records_to_update[folio_origen] = {
                'status': viatico.get('62aa1fa92c20405af671d124', ''),
                'monto_autorizado': viatico.get('627bf0d5c651931d3c7eedd3', 0),
                'motivo_no_autorizado': viatico.get('64a06441c375083cb0da8d4f', None),
                'metodo_pago': viatico.get('5893798cb43fdd4b53ab6e1e', None),
            }
        entregas_efevo = 0
        res = self.get_gasto_aprovado(dict_records_to_update, update=True)

        print('dict_records_to_update',dict_records_to_update)
        print('res', res)
        reproces = False
        for viatico in answers.get('62aa1ed283d55ab39a49bd2d', []):
            folio_origen = viatico.get('62aa1fa92c20405af671d120', '')
            if res.get(folio_origen):
                print('status code', res[folio_origen]['status_code'])
                if res[folio_origen]['status_code'] != 202:
                    viatico['62aa1fa92c20405af671d124'] = 'en_proceso'
                    dict_records_to_update.pop(folio_origen)
                    reproces = True

        if reproces:
            res = self.get_gasto_aprovado(dict_records_to_update, update=False)

        print('res2', res)
        answers['649d02057880ff495300bcc0'] = res['anticipo'] 
        answers['629fb33a8758b5808890b22e'] = res['gasto_ejecutado_aprovado'] 
        answers['649d02057880ff495311bcc0'] = res['gasto_ejecutado_efevo_aprovado'] 
        answers['649d02057880ff495300bcc1'] = res['anticipo'] - res['gasto_ejecutado_efevo_aprovado'] 

        return answers
