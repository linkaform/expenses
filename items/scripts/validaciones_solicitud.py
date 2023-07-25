# -*- coding: utf-8 -*-
import sys, wget, bson, simplejson
from datetime import datetime, date

#from linkaform_api import settings, utils
from linkaform_api import settings, lkf_models, network

from account_settings import *


def get_restricted_date(fecha):
    match_query  = {
            'form_id': lkm.form_id('dia_con_restricciones', 'id'),
            'deleted_at': {'$exists': False},
            'answers.64bd87faf3eeaac79345e091': fecha
        }
    print('match_query', match_query)
    records = cr.find(match_query,{'answers':1, 'folio':1})
    return [r for r in records]

def validaciones_solicitud(current_record):
    answers = current_record.get('answers')
    destino = answers.get('61041b50d9ee55ab14965000')
    transporte = answers.get('61041b50d9ee55ab14965ba4')
    costo_transporte = answers.get('61041c9a9242368dd3965da1',0)
    dia_salida = answers.get('61041b50d9ee55ab14965ba2')
    dia_regreso = answers.get('61041b50d9ee55ab14965ba3')
    print('dia salida', dia_salida)

    msg_error_app = {}
    if get_restricted_date(dia_salida):
          msg_error_app.update({
            "61041b50d9ee55ab14965ba2":{
                "msg": [f"La fecha {dia_salida} fue restringida por tu administrador para viajar."], 
                "label": "Fecha de Salida", "error":[]},
            })
    if get_restricted_date(dia_regreso):
          msg_error_app.update({
            "61041b50d9ee55ab14965ba3":{
                "msg": [f"La fecha {dia_regreso} fue restringida por tu administrador para viajar."], 
                "label": "Fecha de Regreso", "error":[]},
            })
    if msg_error_app:
            raise Exception(simplejson.dumps(msg_error_app))
    dia_salida_s = dia_salida.split('-')
    dia_regreso_s = dia_regreso.split('-')
    dia = date(int(dia_salida_s[0]),int(dia_salida_s[1]),int(dia_salida_s[2]))
    dia_r = date(int(dia_regreso_s[0]),int(dia_regreso_s[1]),int(dia_regreso_s[2]))
    cant_dias = (dia_r - dia).days
    answers['61041d15d9ee55ab14965bb5'] = cant_dias
    if cant_dias < 0:
        msg_error_app.update({
                "61041b50d9ee55ab14965ba2":{
                    "msg": [f"La fecha de salida {dia_salida}, debe de ser mayor que la fecah de regreso{dia_regreso}."], 
                    "label": "Fecha de Salida", "error":[]},
            })
    if destino == 'cabuyaro':
        print('transporte=', transporte)
        if transporte not in ('auto_empresa', 'bus'):
            msg_error_app.update({
                "61041b50d9ee55ab14965ba4":{
                    "msg": [f"Para viajar a Cabyuaro solo es permitido seleccionar como Medio de Transporte Bus o Auto Empresa."], 
                    "label": "Medio de Transporte", "error":[]},
            })
        if dia.weekday() != 1 and dia.weekday() != 4:
            msg_error_app.update({
                "61041b50d9ee55ab14965ba2":{"msg": [f"El dia de salida solo puede ser Martes o Viernes "], "label": "Fecha de Salida", "error":[]},
            })
        if dia_r.weekday() != 1 and dia_r.weekday() != 4:
            msg_error_app.update({
                "61041b50d9ee55ab14965ba3":{"msg": [f"El dia de regreso solo puede ser Martes o Viernes "], "label": "Fecha de Regreso", "error":[]},
            })
        if costo_transporte > 0:
            msg_error_app.update({
                "61041c9a9242368dd3965da1":{
                    "msg": [f"Al viajar a Cabyuaro el costo de transporte debe de ser $0."], 
                    "label": "Costo Transporte", "error":[]},
            })
    if msg_error_app:
            raise Exception(simplejson.dumps(msg_error_app))

    if destino != 'otro':
        answers['61041b50d9ee55ab14965ba0'] = destino.title()
    return answers

if __name__ == '__main__':
    print(sys.argv)
    current_record = simplejson.loads(sys.argv[1])
    total_global = 0
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    lkm = lkf_models.LKFModules(settings)
    net = network.Network(settings)
    cr = net.get_collections()

    if not current_record.get('answers'):
        current_record = read_current_record_from_txt( current_record['answers_url'] )

    current_record['answers'] = validaciones_solicitud(current_record)
   
    sys.stdout.write(simplejson.dumps({
        'status': 101,
        'replace_ans': current_record['answers']
    }))