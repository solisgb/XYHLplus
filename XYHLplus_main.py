# -*- coding: Latin-1 -*-
"""
Script para hacer graficos temporales con lineas horizontales

@solis
"""
import traceback
import logging

FILE_INI_XML = 'XYHL.xml'

if __name__ == "__main__":

    try:
        from datetime import timedelta
        from time import time
        from XYHL import select_project, make_graphs

        project = select_project(FILE_INI_XML)
        startTime = time()

        make_graphs(project)

        xtime = time()-startTime
        print('The script took {0}'.format(str(timedelta(seconds=xtime))))
    except Exception as e:
        logging.error(traceback.format_exc())
    finally:
        print('fin')
