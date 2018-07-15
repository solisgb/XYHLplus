# -*- coding: Latin-1 -*-
"""
Created on Tue May  1 10:54:23 2018

@author: solis
"""

import log_file as lf


def select_project(FILENAME):
    """
    returns the selected project
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(FILENAME)
    root = tree.getroot()

    print('Projects in ' + FILENAME)
    projects = []
    for i, project in enumerate(root.findall('project')):
        projects.append(project)
        print(i, end=' ')
        print('. ' + project.get('name'))
    print('Select project number:')
    choice = input()
    return projects[int(choice)]


def make_graphs(project):
    """
    selecciona los patos para los gráficos y llama a lafunción que dibuja
    los gráficos con el modulo matplotlib

    input
        project: es el tag del fichero XYplus_parameters.f_xml seleccionado
            en XYplus_main
    """
    from os.path import join
    import pyodbc
    import db_con_str
    import XYplus_parameters as par

    db = project.find('db').text
    con = pyodbc.connect(db_con_str.con_str(db))

    cur = con.cursor()
    select_master = project.find('select_master').text.strip()
    cur.execute(select_master)

    select_data = project.find('select_data').text.strip()
    npar = select_data.count('?')
    if npar != 1:
        raise ValueError('select_data debe tener un signo ?')
    id_col = int(project.find('select_master').get('id_column')) - 1

    cur2 = con.cursor()
    fecha_col = int(project.find('select_data').get('fecha_column')) - 1
    value_col = int(project.find('select_data').get('value_column')) - 1
    dir_out = project.find('dir_out').text.strip()
    ylabel = project.find('graph').get('y_axis_name')
    for row in cur:

        # datos de la serie
        print(row[id_col])
        cur2.execute(select_data, row[id_col])
        xy = [(row_data[fecha_col], row_data[value_col]) for row_data in cur2]
        if len(xy) == 0:
            print('{0} no tiene datos'.format(row[id_col]))
            continue
        fechas = [xy1[0] for xy1 in xy]
        values = [xy1[1] for xy1 in xy]

        # datos de los umbrales
        if par.show_hl == 1:
            fechas_u, values_u, legends_u = _umbrales_get(project, row[id_col],
                                                          cur2, fechas[0],
                                                          fechas[-1])

        # elementos adicionales del gráfico
        stitle = get_title(project, row)
        legend_master = legend_master_get(project, row)
        file_name = file_name_get(project, row)
        dst = join(dir_out, file_name)

        if len(values_u) == 0:
            XYt_1(fechas, values, legend_master, stitle, ylabel, dst)
        else:
            XYt_1(fechas, values, legend_master, stitle, ylabel, dst,
                  fechas_u, values_u, legends_u)

    con.close()


def _umbrales_get(project, id1, cur2, fecha1, fecha2):
    """
    selecciona los datos del umbral o umbrales

    input:
        project: tag del proyecto seleccionado
        id1: código del punto cuyos umbrales cuyos queremos representar
        row: fila de select_master correspondiente al punto cuyos umbrales
            queremos representar
        cur2: cursor a la BDD para seleccionar los datos

    return:
        fechas_u: [[d1,d2],...n] n es el número de umbrales de id1
                  [d1,d1] d1 es el date del umbral 1 de id1 y d2 es un
                  date del umbral 1 de id1
        values_u: [[u1,u1],...n] n es el número de umbrales de id1
                  [u1,u1] u1 es el umbral 1 de id1
        legends_u: [leg1,...n]  n es el número de umbrales de id1
                   leg1 es la leyenda 1 del umbral 1 de id1
    """
    select_umbrales = project.find('select_umbrales').text.strip()
    umbral_col = int(project.find('select_umbrales').get('umbral_column')) - 1
    if select_umbrales.count('?') != 3:
        raise ValueError('select_umbrales debe tener 3 signos ?')

    fechas_u = []
    values_u = []
    legends_u = []
    for i, umbral in enumerate(project.findall('select_umbrales/umbral')):
        parametro = umbral.get('parametro').strip()
        cod_u = umbral.get('cod').strip()
        cur2.execute(select_umbrales, (id1, cod_u, parametro))
        row1_u = cur2.fetchone()
        if row1_u is None:
            lf.write('{} no tiene umbral: {}, {}'.format(id1, cod_u,
                     parametro))
            continue
        # todos los umbrales se ponen en el rango de fechas de cada sondeo
        # si se desea ponerlo en su rango específico debe escribirse una
        # función ad hoc extrayendo los datos de la tabla umbrales
        fechas_u.append([fecha1, fecha2])
        values_u.append([row1_u[umbral_col], row1_u[umbral_col]])
        legends_u.append(legends_umbrales_get(project, row1_u, i))
    if not values_u:
        lf.write('{0} no tiene umbrales'.format(id1))
        return [], [], []
    return fechas_u, values_u, legends_u


def get_title(project, row):
    """
    forma el título de un gráfico

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row: es fila activa devuelta por select_master) de donde se
            extrae el título del gráfico

    return
        un str con el título del gráfico (puede tener más de una línea)
    """
    titles = project.findall('graph/title')
    if len(titles) == 0:
        return ""
    stitles = [title.text.strip() for title in titles]
    for i, title in enumerate(titles):
        cols = title.findall('column')
        if len(cols) == 0:
            continue
        subs = [row[int(col.text)-1] for col in cols]
        stitles[i] = stitles[i].format(*subs)
    return '\n'.join(stitles)


def legend_master_get(project, row):
    """
    forma la leyenda de la serie principal del gráfico

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row: es fila activa devuelta por select_master) de donde se
            extrae el título del gráfico

    return
        un str con la leyenda del punto principal del gráfico
    """
    legend_master = project.find('graph/legend_master').text.strip()
    columns_master = project.findall('graph/legend_master/column')
    if len(columns_master) == 0:
        return legend_master
    subs = [row[int(col1.text)-1] for col1 in columns_master]
    return legend_master.format(*subs)


def legends_umbrales_get(project, row1_u, ilegend):
    """
    forma la leyenda de uno de los umbrales

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row1_u: es la fila devuelta para un punto después de ejecutar la
            select select_umbrales del fichero XYplus_parameters.f_xml
        ilegend: es un int que define el número de umbral para el punto

    return
        un str con la leyenda
    """
    legend_tag = project.find('graph/legend_umbrales')
    legend_mold = legend_tag.text.strip()
    len_legend_mold = len(legend_mold)
    col_tags = legend_tag.findall('column')
    n_cols = len(col_tags)
    if len_legend_mold == 0:
        return 'Leg. {0:d}'.format(ilegend)
    else:
        if n_cols == 0:
            return legend_mold
        else:
            subs = [row1_u[int(col.text)-1] for col in col_tags]
            return legend_mold.format(*subs)


def file_name_get(project, row):
    """
    forma el nombre de cada fichero de gráfico

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row: es la fila de un punto que devuelve la select
            select_master del fichero XYplus_parameters.f_xml

    return
        sname: str que contiene el nombre del fichero
    """
    fname = project.find('select_master/file_name').text.strip()
    tcols = project.findall('select_master/file_name/column')
    subs = [row[int(tcol.text)-1] for tcol in tcols]
    sname = fname.format(*subs)
    return sname


def XYt_1(fechas, values, legend_master, fechas_u, values_u, legends_umbrales,
          stitle, ylabel, dst):
    """
    dibuja un gráfico xy de una o más series

    input
        fechas: [d1, ...n] d1 elemento date, donde n es la longitud de
            la serie
        values: [v1, ...n] v1 elemento float, donde n es la longitud de
            la serie
        legend_master_get: leyenda de la serie principal
        stitle: título del gráfico
        ylabel: título del eje Y
        dst: directorio donde se graba el gráfico (debe existir)
        fechas_u
        values_u
        legends_u
    """
    import matplotlib.pyplot as mpl
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    dateFmt = mdates.DateFormatter('%d-%m-%Y')

    fig, ax = plt.subplots()
    ax.plot(fechas, values, marker='.', label=legend_master)
    for i, vu1 in enumerate(values_u):
        ax.plot(fechas_u, vu1, label=legends_umbrales[i])

    plt.ylabel(ylabel)
    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)
    mpl.legend(loc='best', framealpha=0.5)
    mpl.legend(loc='best', framealpha=0.5)
    mpl.tight_layout()
    mpl.grid(True)

    fig.savefig(dst)
    plt.close('all')


def validate_parameters():
    """
    comprueba la validez de las variables definidas en el módulo
        XYplus_parameters
    """
    import XYplus_parameters as par
    from os.path import isdir, exists

    def validate_date(sdate: str, variable_name: str):
        """
        a partir de un str con formato "dd/mm/yyyy" devuelve un objeto date
        """
        from datetime import date
        if sdate == 'now':
            sdate = date.today().strftime('%d/%m/%Y')
        ws = sdate.split('/')
        try:
            return date(int(ws[2]), int(ws[1]), int(ws[0]))
        except Exception as error:
            raise ValueError('La variable {} está mal escrita'.
                             format(variable_name))

    if not exists(par.f_xml):
        raise ValueError('No existe {}'.format(par.f_xml))
    if not isdir(par.dir_out):
        raise ValueError('No existe {}'.format(par.dir_out))
    if par.show_hl not in (0, 1):
        raise ValueError('La variable show_hl debe ser 0 o 1')
    if par.show_aux not in (0, 1):
        raise ValueError('La variable show_aux debe ser 0 o 1')
    par.date_1 = validate_date(par.date_1, 'date_1')
    par.date_2 = validate_date(par.date_2, 'date_2')
    if par.date_1 >= par.date_2:
        raise ValueError('date_1 debe ser < que date_2')

    class Serie_temporal():
        """
        define los datos y sus atributos para ser representados en un
            gráfico
        """
        def __init__(self, fechas: [], values: [], legends: [],
                     markers: []):
            """
            fechas: cada elemento una lista de dates
            """
            pass
