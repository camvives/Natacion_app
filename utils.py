"""Collection of utility functions for common tasks. 
This simplify common operations and improve code readability"""

from math import ceil
from collections import defaultdict
import random

def convert_timestamp(mm_values: list, ss_values:list, sss_values:list):
    """Returns a list with timestamps formatted in mm:ss:sss or '99:99:999' 
        if any value is empty."""

    zipped_times = zip(mm_values, ss_values, sss_values)
    formatted_times = []

    for minu, sec, sss in zipped_times:
        if '' in (minu, sec, sss):
            last_digits = random.randint(0, 100)
            formatted_times.append(f'99:99:{int(last_digits):02}')
        else:
            formatted_times.append(f'{int(minu):02}:{int(sec):02}:{int(sss):02}')

    return formatted_times

def convert_one_timestamp(minu:str, sec:str, sss:str):
    """Converts values into timestamp mm:ss:sss"""

    timestamp = f'{int(minu):02}:{int(sec):02}:{int(sss):03}'

    return timestamp

def order_swimmers_comp(nadadores_prueba: list):
    """Asign a pool number and a lane number for each swimmer in an event"""
    nadadores_prueba = [list(row) for row in nadadores_prueba]
    cant_nadadores = len(nadadores_prueba)
    list_carril = [4,3,5,2,6,1]

    cant_piletas = ceil(cant_nadadores / 6)

    for i in range(cant_piletas):
        start_index = i * 6
        end_index = min((i + 1) * 6, cant_nadadores)

        for j, k in zip(range(start_index, end_index), list_carril):
            nadadores_prueba[j][3] = cant_piletas - i
            nadadores_prueba[j][4] = k

    # Get the swimmers for the last pool
    ultima_pileta = [sublist for sublist in nadadores_prueba if sublist[-2] == 1]
    cant_ult_pileta = len(ultima_pileta)

    if cant_nadadores > 6 and cant_ult_pileta < 5:
        if cant_ult_pileta < 3:
            nadadores_prueba[-(cant_ult_pileta + 2)][3] = 1
        nadadores_prueba[-(cant_ult_pileta + 1)][3] = 1

    ultima_pileta = [sublist for sublist in nadadores_prueba if sublist[-2] == 1]
    cant_ant = len(nadadores_prueba) - len(ultima_pileta)

    for j, k in zip(range(cant_ant, cant_nadadores), list_carril):
        nadadores_prueba[j][4] = k


    return nadadores_prueba

def get_orden(row):
    """Returns orden of swimmer"""
    return row['Orden']

def order_pools(nadadores_prueba: list):
    """Order swimmers into diferents pools for an event"""

    # Create a defaultdict with the default value as a list
    grouped_sublists = defaultdict(list)

    for sublist in nadadores_prueba:
        key = sublist[-2]
        grouped_sublists[key].append(sublist)

    result = list(grouped_sublists.values())

    piletas = []
    for pileta in result:
        pileta.sort(key=get_orden)
        piletas.append(pileta)

    piletas.reverse()

    return piletas


def order_swimmers_rec(nadadores_pruebas: list):
    """Asign randomly a pool number and a lane number for each swimmer in an event"""
    return nadadores_pruebas
