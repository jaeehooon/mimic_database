

"""
This file is for patient's encounter(visit, admission) inforamtion.
It has 'HospitalEncounter', 'ICUEncounter' class for admission.

"""

#
# class HospitalEncounter(object):
#
#     def __init__(self, patient_obj, hadm_id, is_for_blood_test=0, age=None,
#                  admit_dx=None, admit_time=None, disch_time=None, death_time=None,
#                  admit_type=None, admit_loc=None, disch_loc=None,
#                  marital_status=None, ethnicity=None, insurance=None, language=None,
#                  hospital_expire_flag=None, has_chartevents=None):
#
#         self.patient_obj = patient_obj
#         self.hadm_id = hadm_id
#         self.is_for_blood_test = is_for_blood_test              # Is only admission for 'blood test' (Only Lab Result)
#         self.admit_dx = admit_dx                                # Hospital Admission Diagnosis
#         self.admit_time = admit_time                            # Hospital Admission Time
#         self.disch_time = disch_time                            # Hospital Discharge Time
#         self.death_time = death_time
#         self.admit_type = admit_type                            # Admission Type
#         self.admit_loc = admit_loc                              # Admission Location
#         self.disch_loc = disch_loc                              # Discharge Location
#
#         # 시간 단위
#         self.los = (((disch_time - admit_time).days * 24 * 60 * 60) +
#                     (disch_time - admit_time).seconds) / 60 / 60
#
#         self.hadm_age = age                                     # age when a patient visits
#         self.hadm_marital_status = marital_status               # Marital Status
#         self.hadm_ethnicity = ethnicity                         # Ethnicity
#         self.hadm_insurance = insurance                         # Insurance
#         self.hadm_language = language                           # Language
#
#         self.readmission = 0                                    # This visit is whether re-admission or not
#         self.hospital_expire_flag = hospital_expire_flag        # Whether the patient's expired in the visit
#         self.has_chartevents = has_chartevents
#
#         # records
#         self.dx_list = None
#         self.drg_list = None
#         self.rx_list = None
#         self.proc_list = None
#         self.labevent_list = None


def hospital_encounter(patient_obj, hadm_id, is_for_blood_test=0, age=None,
                       admit_dx=None, admit_time=None, disch_time=None, death_time=None,
                       admit_type=None, admit_loc=None, disch_loc=None,
                       marital_status=None, ethnicity=None, insurance=None, language=None,
                       hospital_expire_flag=None, has_chartevents=None):
    """
    This method is for generating hospital encounter dictionary.
    """
    hospital_counter = {
        'patient_obj': patient_obj,
        'hadm_id': hadm_id,
        'is_for_blood_test': is_for_blood_test,
        'admit_dx': admit_dx,
        'admit_time': admit_time,
        'disch_time': disch_time,
        'death_time': death_time,
        'admit_type': admit_type,
        'admit_loc': admit_loc,
        'disch_loc': disch_loc,

        'los': (((disch_time - admit_time).days * 24 * 60 * 60) +
                (disch_time - admit_time).seconds) / 60 / 60,

        'hadm_age': age,                                        # age when a patient visits
        'hadm_marital_status': marital_status,                  # Marital Status
        'hadm_ethnicity': ethnicity,                            # Ethnicity
        'hadm_insurance': insurance,                            # Insurance
        'hadm_language': language,                              # Language

        'readmission': 0,                                       # This visit is whether re-admission or not
        'hospital_expire_flag': hospital_expire_flag,           # Whether the patient's expired in the visit
        'has_chartevents': has_chartevents,

        'dx_list': None,
        'drg_list': None,
        'rx_list': None,
        'proc_list': None,
        'lab_list': None
    }

    return hospital_counter
