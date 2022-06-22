"""
This file is for patient's encounter(visit, admission) inforamtion.
It has 'HospitalEncounter', 'ICUEncounter' class for admission.

"""
from mimic_iii.medical_record import *


class HospitalEncounter(object):

    def __init__(self, patient_obj, hadm_id, is_for_blood_test=0, age=None,
                 admit_dx=None, admit_time=None, disch_time=None, death_time=None,
                 admit_type=None, admit_loc=None, disch_loc=None,
                 marital_status=None, ethnicity=None, insurance=None, language=None,
                 hospital_expire_flag=None, has_chartevents=None):

        self.patient_obj = patient_obj
        self.hadm_id = hadm_id
        self.is_for_blood_test = is_for_blood_test              # Is only admission for 'blood test' (Lab Result)
        self.admit_dx = admit_dx                                # Hospital Admission Diagnosis
        self.admit_time = admit_time                            # Hospital Admission Time
        self.disch_time = disch_time                            # Hospital Discharge Time
        self.death_time = death_time
        self.admit_type = admit_type                            # Admission Type
        self.admit_loc = admit_loc                              # Admission Location
        self.disch_loc = disch_loc                              # Discharge Location

        # 시간 단위
        self.los = (((disch_time - admit_time).days * 24 * 60 * 60) +
                    (disch_time - admit_time).seconds) / 60 / 60

        self.hadm_age = age                                     # age when a patient visits
        self.hadm_marital_status = marital_status               # Marital Status
        self.hadm_ethnicity = ethnicity                         # Ethnicity
        self.hadm_insurance = insurance                         # Insurance
        self.hadm_language = language                           # Language

        self.readmission = 0                                    # This visit is whether re-admission or not
        self.hospital_expire_flag = hospital_expire_flag        # Whether the patient's expired in the visit
        self.has_chartevents = has_chartevents

        # records
        self.dx_list = None
        self.drg_list = None
        self.rx_list = None
        self.proc_list = None
        self.labevent_list = None

        self.total_icu_stays = 0

    # def update_demographic(self):
    #     self.marital_status = self.hadm_marital_status
    #     self.ethnicity = self.hadm_ethnicity
    #     self.insurance = self.hadm_insurance
    #     self.language = self.hadm_language
    #     self.expired = self.hospital_expire_flag
    #
    # def set_patient_info(self, patient_obj):
    #     subject_id, gender, _, marital_status, \
    #         ethnicity, insurance, language, expired = patient_obj.get_patient_info()
    #
    #     self.subject_id = subject_id
    #     self.gender = gender


class ICUEncounter(object):
    def __init__(self, subject_id, hadm_id):
        pass
