# -*- coding: utf-8 -*-
import sys, wget, bson, simplejson
from datetime import datetime, date

#from linkaform_api import settings, utils
from account_settings import *

def validaciones_solicitud(current_record):
    answers = current_record.get('answers')
    destino = answers.get('61041b50d9ee55ab14965000')
    transporte = answers.get('61041b50d9ee55ab14965ba4')
    costo_transporte = answers.get('61041c9a9242368dd3965da1',0)
    dia_salida = answers.get('61041b50d9ee55ab14965ba2').split('-')
    print('dia salida', dia_salida)
    dia = date(int(dia_salida[0]),int(dia_salida[1]),int(dia_salida[2]))
    print('dia salida', dia)
    print('dia salida', dia.weekday())
    if dia.weekday() != 1 and dia.weekday() != 4:
        msg_error_app = {
            "61041b50d9ee55ab14965ba2":{"msg": [f"El dia de salida solo puede ser Martes o Viernes "], "label": "Fecha de Salida", "error":[]},
        }
        raise Exception(simplejson.dumps(msg_error_app))
    if destino == 'cabuyaro':
        print('transporte=', transporte)
        if transporte not in ('auto_empresa', 'bus'):
            msg_error_app = {
                "61041b50d9ee55ab14965ba4":{
                    "msg": [f"Para viajar a Cabyuaro solo es permitido seleccionar como Medio de Transporte Bus o Auto Empresa."], 
                    "label": "Medio de Transporte", "error":[]},
            }
            raise Exception(simplejson.dumps(msg_error_app))
        if costo_transporte > 0:
            msg_error_app = {
                "61041c9a9242368dd3965da1":{
                    "msg": [f"Al viajar a Cabyuaro el costo de transporte debe de ser $0."], 
                    "label": "Costo Transporte", "error":[]},
            }
            raise Exception(simplejson.dumps(msg_error_app))
    if destino != 'otro':
        answers['61041b50d9ee55ab14965ba0'] = destino.title()
    return answers

if __name__ == '__main__':
    print(sys.argv)
    current_record = simplejson.loads(sys.argv[1])
    total_global = 0
    
    if not current_record.get('answers'):
        current_record = read_current_record_from_txt( current_record['answers_url'] )

    current_record['answers'] = validaciones_solicitud(current_record)
   
    sys.stdout.write(simplejson.dumps({
        'status': 101,
        'replace_ans': current_record['answers']
    }))