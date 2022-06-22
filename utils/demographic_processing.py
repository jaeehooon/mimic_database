import numpy as np


def process_marital(value):
    """
    processing 'Marital Status' feature in MIMIC-III dataset
    """
    if value in [np.nan, '', None, 'UNKNOWN (DEFAULT)']:
        result = 'UNKNOWN'
    else:
        result = value
    return result


def process_ethnicity(value):
    """
    processing 'Ethnicity' feature in MIMIC-III dataset
    """

    if 'ASIAN' in value:
        result = 'ASIAN'
    elif 'WHITE' in value:
        result = 'WHITE'
    elif 'BLACK' in value:
        result = 'BLACK'
    elif 'HISPANIC' in value:
        result = 'HISPANIC'
    elif value in ['UNKNOWN/NOT SPECIFIED', 'UNABLE TO OBTAIN', 'PATIENT DECLINED TO ANSWER']:
        result = 'UNKNOWN'
    elif 'AMERICAN INDIAN' in value:
        result = 'AMERICAN INDIAN'
    elif value in ['CARIBBEAN ISLAND', 'NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER', 'SOUTH AMERICAN']:
        result = 'AMERICAN INDIAN'
    else:
        result = value

    return result
