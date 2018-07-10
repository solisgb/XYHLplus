# -*- coding: Latin-1 -*-
"""
Created on Tue Jul 10 19:35:33 2018

@author: solis
"""
# PARAMETERS

# fichero xml de configuracion de proyectos
f_xml = 'XYHLplus.xml'

# Directorio de salida
dir_out = r'E:\WORK\CHS\Mingogil\xy'

# grabar lineas horizontales (1: s�, 0: no)
show_hl = 0

# grabar series auxiliares upper plot
show_aux = 1

# rangos de fechas (formato dd/mm/yyyy) date1<date2
# date_2 puede tener el valor 'now', en cuyo caso se sustituye internamente
# por la fecha de ejecuci�n
date_1 = '1/1/1900'
date_2 = 'now'


def validate_parameters():
    """
    valida que los valores de los par�metros son correctos
    """
    """
    comprueba la validez de los par�metros
    """
    from os.path import isdir, exists
    from datetime import date
    if not exists(f_xml):
        raise ValueError('No existe {}'.format(f_xml))
    if not isdir(dir_out):
        raise ValueError('No existe {}'.format(dir_out))
    if show_hl not in (0, 1):
        raise ValueError('La variable show_hl debe ser 0 o 1')
    if show_aux not in (0, 1):
        raise ValueError('La variable show_aux debe ser 0 o 1')
    ws = date_1.split('/')
    try:
        date_1 = date(int(ws[2]), int(ws[1]), int(ws[0]))
    except Exception as error:
        raise ValueError('La variable date_1 est� mal escrita')
