# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 09:22:00 2018
@author: Luis Solis
Serie temporal para gráficos con el módulo matplotlib
"""

import numpy as np


class Time_series():
    """
    define los datos y sus atributos para ser representados en un
        gráfico
    """
    def __init__(self, fechas: [], values: [], legend: str,
                 marker: str):
        """
        fechas: cada elemento una lista de dates
        values: cada elemento una lista de floats o integeres
        legend: leyenda de la serie
        marker: marcador de la serie en el gráfico
        """
        if len(fechas) != len(values):
            raise ValueError('fechas y values != longitud')
        self.fechas = np.array(fechas)
        self.values = np.array(values)
        self.legend = legend
        self.marker = marker
