# -*- coding: utf-8 -*-
import sys, wget, bson, simplejson
from datetime import datetime, date

#from expense_utils import Expenses
from lkf_addons.addons.expenses.expense_utils import Expenses

from account_settings import *

class Expenses(Expenses):

    def get_restricted_date(self, fecha):
        match_query  = {
                'form_id': self.lkm.form_id('dia_con_restricciones', 'id'),
                'deleted_at': {'$exists': False},
                'answers.64bd87faf3eeaac79345e091': fecha
            }
        print('match_query', match_query)
        records = self.cr.find(match_query,{'answers':1, 'folio':1})
        return [r for r in records]

    def validaciones_solicitud(self, answers):
        print('entra... >>>>>>>>>>>>>>>>>>>>>>>')
        answers = super().validaciones_solicitud(answers)
        print('validacion asi regrsea <<<<<<<<<<<<<<<<<<<<<')
        destino = answers.get('61041b50d9ee55ab14965000')
        transporte = answers.get('61041b50d9ee55ab14965ba4')
        costo_transporte = answers.get('61041c9a9242368dd3965da1',0)
        dia_salida = answers.get('61041b50d9ee55ab14965ba2')
        dia_regreso = answers.get('61041b50d9ee55ab14965ba3')
        msg_error_app = {}
        dia_salida_s = dia_salida.split('-')
        dia_regreso_s = dia_regreso.split('-')
        dia = date(int(dia_salida_s[0]),int(dia_salida_s[1]),int(dia_salida_s[2]))
        dia_r = date(int(dia_regreso_s[0]),int(dia_regreso_s[1]),int(dia_regreso_s[2]))

        if self.get_restricted_date(dia_salida):
              msg_error_app.update({
                "61041b50d9ee55ab14965ba2":{
                    "msg": [f"La fecha {dia_salida} fue restringida por tu administrador para viajar."], 
                    "label": "Fecha de Salida", "error":[]},
                })

        if self.get_restricted_date(dia_regreso):
              msg_error_app.update({
                "61041b50d9ee55ab14965ba3":{
                    "msg": [f"La fecha {dia_regreso} fue restringida por tu administrador para viajar."], 
                    "label": "Fecha de Regreso", "error":[]},
                })
        if msg_error_app:
                raise Exception(simplejson.dumps(msg_error_app))

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
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    expense_obj = Expenses(settings)

    current_record['answers'] = expense_obj.validaciones_solicitud(current_record['answers'])
   
    sys.stdout.write(simplejson.dumps({
        'status': 101,
        'replace_ans': current_record['answers']
    }))