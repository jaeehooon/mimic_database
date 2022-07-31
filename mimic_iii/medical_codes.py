"""


"""


def dx_record(hadm_id, icd_version):
    dx_dict = {
        'hadm_id': hadm_id,
        'icd_version': icd_version,
        'elements': []
    }
    return dx_dict


def drg_record(hadm_id):
    drg_list = {
        'hadm_id': hadm_id,
        'elements': []
    }
    return drg_list


def add_element(record_dict, item, medical_code=''):
    if medical_code not in ['rx', 'proc', 'dx', 'lab']:
        raise f"Wrong medical code type! You input {medical_code} as medical code"

    if medical_code == 'rx':
        drug, fdc, drug_type, route = item

        rx_item = {
            'drug': drug,
            'fdc': fdc,
            'type': drug_type,
            'route': route
        }
        record_dict['elements'].append(rx_item)
    elif medical_code == 'lab':
        (chart_time, item_id, flag) = item

        if chart_time not in record_dict:
            record_dict[chart_time] = []
        record_dict[chart_time].append((item_id, flag))
    else:
        record_dict['elements'].append(item)

    return record_dict


def rx_record(hadm_id):
    rx_list = {
        'hadm_id': hadm_id,
        'elements': []
    }
    return rx_list


def proc_record(hadm_id, icd_version):
    proc_list = {
        'hadm_id': hadm_id,
        'icd_version': icd_version,
        'elements': []
    }
    return proc_list


def add_rx_element(rx_dict, item):
    drug, fdc, drug_type, route = item

    rx_item = {
        'drug': drug,
        'fdc': fdc,
        'type': drug_type,
        'route': route
    }
    rx_dict['elements'].append(rx_item)

    return rx_dict


def lab_record(hadm_id):
    lab_event_list = {
        'hadm_id': hadm_id,
        'elements': {}
    }
    return lab_event_list


def add_lab_element(lab_dict, item):
    (chart_time, item_id, flag) = item

    if chart_time not in lab_dict:
        lab_dict[chart_time] = []
    lab_dict[chart_time].append((item_id, flag))

    return lab_dict
