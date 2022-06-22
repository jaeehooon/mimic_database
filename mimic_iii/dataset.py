import os
import pickle
import csv
import numpy as np
import sys
from datetime import datetime
from tqdm.auto import tqdm

from mimic_iii.patients import Patient
from mimic_iii.medical_record import *
from mimic_iii.encounter import HospitalEncounter, ICUEncounter
from utils.convert import ICDCodeConverter
from utils.demographic_processing import *
from utils.utils import *


class MIMICDataset(object):
    def __init__(self, version):
        self.mimic_data = {}
        """
        전체 MIMIC-III 데이터셋
            in-hospitalization,
                Max Num Dx: 39
                Max Num Rx: 1400
                Max Num Proc: 65
                Max Num Lab: 1169
            Avg. Dx: 11.04
            Avg. Rx: 70.48
            Avg. Proc: 4.07
            Avg. Lab: 28.22
            
        """
        self.icd_version = version
        self.icd_converter = ICDCodeConverter()

    def process_patient(self, infile):
        """
        Process Patient Info function
        This method processes patient's information from 'PATIENTS.csv'
        """
        print("processing patient table....")
        inff = open(infile, 'r')
        for line in csv.DictReader(inff):
            patient_id = line['SUBJECT_ID']

            if patient_id in self.mimic_data:
                continue

            dob = datetime.strptime(line['DOB'], "%Y-%m-%d %H:%M:%S")
            try:
                dod = datetime.strptime(line['DOD'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dod = None

            gender = line['GENDER']
            expired = line['EXPIRE_FLAG']

            self.mimic_data[patient_id] = {
                'patient': Patient(
                    subject_id=patient_id,
                    gender=gender,
                    dob=dob,
                    dod=dod,
                    expired=expired
                ),
                'admissions': {},
                'icu_stays': {}
            }

        inff.close()
        print('')
        return self.mimic_data

    def process_admission(self, infile):
        """
        Process admission information function
        This method processes patient's encounter(visit, admission, hospitalization) information from 'ADMISSIONS.csv'

        """
        print("processing admission table...")

        inff = open(infile, 'r')
        count = 0
        for line in csv.DictReader(inff):

            patient_id = line['SUBJECT_ID']
            if patient_id not in self.mimic_data:
                patient_obj = Patient(patient_id)
                self.mimic_data[patient_id] = {
                    'patient': patient_obj,
                    'admissions': {},
                    'icu_stays': {}
                }
            else:
                patient_obj = self.mimic_data[patient_id]['patient']

            hadm_id = line['HADM_ID']
            admit_dx = "None"
            admit_time = datetime.strptime(line['ADMITTIME'], "%Y-%m-%d %H:%M:%S")
            disch_time = datetime.strptime(line['DISCHTIME'], "%Y-%m-%d %H:%M:%S")
            admit_type = line['ADMISSION_TYPE']
            admit_loc = line['ADMISSION_LOCATION']
            disch_loc = line['DISCHARGE_LOCATION']
            ethnicity = process_ethnicity(line['ETHNICITY'])
            # if line['ETHNICITY'] in [np.nan, '', None, 'UNOBTAINABLE', 'NOT SPECIFIED']:
            #     ethnicity = "UNKNOWN"
            # else:
            #     ethnicity = line['ETHNICITY']

            insurance = line['INSURANCE']
            # if line['INSURANCE'] in [np.nan, '', None, 'PATIENT DECLINED TO ANSWER', 'UNABLE TO OBTAIN']:
            #     insurance = "UNKNOWN"
            # else:
            #     insurance = line['INSURANCE']

            marital_status = process_marital(line['MARITAL_STATUS'])
            # if line['MARITAL_STATUS'] in [np.nan, '', None, 'UNKNOWN (DEFAULT)']:
            #     marital_status = 'UNKNOWN'
            # else:
            #     marital_status = line['MARITAL_STATUS']

            expired = line['HOSPITAL_EXPIRE_FLAG']
            has_chartevents = line['HAS_CHARTEVENTS_DATA']

            hadm_age = int((admit_time - patient_obj.dob).days / 365)
            """
            NEWBORN 이 admit_type인 사람:       7,864
            나이가 0살인 사람:                    7,874
            """

            hadm_obj = HospitalEncounter(
                patient_obj=patient_obj,
                hadm_id=hadm_id,
                age=hadm_age,
                admit_dx=admit_dx,
                admit_time=admit_time,
                disch_time=disch_time,
                admit_type=admit_type,
                admit_loc=admit_loc,
                disch_loc=disch_loc,
                ethnicity=ethnicity,
                insurance=insurance,
                marital_status=marital_status,
                hospital_expire_flag=expired,               # flag whether the patient died 'in the hospital'
                has_chartevents=has_chartevents
            )

            self.mimic_data[patient_id]['admissions'][hadm_id] = hadm_obj
            self.mimic_data[patient_id]['patient'].total_stays += hadm_obj.los
            count += 1

        inff.close()
        print('')
        return self.mimic_data

    def process_dx_icd(self, infile):
        print("processing diagnosis_icd table....")
        none_dx = 0
        inff = open(infile, 'r')
        for line in csv.DictReader(inff):
            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            hadm_obj = self.mimic_data[patient_id]['admissions'][hadm_id]

            if hadm_obj.dx_list is None:
                self.mimic_data[patient_id]['admissions'][hadm_id].dx_list = DxRecord(hadm_id, self.icd_version)

            icd_code = self.icd_converter.convert_dx_digit(line['ICD9_CODE'])
            if icd_code is not None:
                self.mimic_data[patient_id]['admissions'][hadm_id].dx_list.add_element(icd_code)
            else:
                none_dx += 1

        inff.close()
        print('\tNone Dx Code: ', none_dx)
        print('')
        return self.mimic_data

    def process_rx(self, infile):
        print("processing prescriptions table...")
        none_rx = 0
        inff = open(infile, 'r')
        for line in csv.DictReader(inff):
            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            hadm_obj = self.mimic_data[patient_id]['admissions'][hadm_id]
            drug = line['DRUG']

            if hadm_obj.rx_list is None:
                self.mimic_data[patient_id]['admissions'][hadm_id].rx_list = RxRecord(hadm_id)
            self.mimic_data[patient_id]['admissions'][hadm_id].rx_list.add_element(drug)

        inff.close()
        print('')

        return self.mimic_data

    def process_proc(self, infile):

        print("processing procedure table....")
        none_proc = 0
        inff = open(infile, 'r')
        for line in csv.DictReader(inff):
            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            hadm_obj = self.mimic_data[patient_id]['admissions'][hadm_id]

            if hadm_obj.proc_list is None:
                self.mimic_data[patient_id]['admissions'][hadm_id].proc_list = ProcRecord(hadm_id, self.icd_version)

            icd_code = self.icd_converter.convert_proc_digit(line['ICD9_CODE'])
            if icd_code is not None:
                self.mimic_data[patient_id]['admissions'][hadm_id].proc_list.add_element(icd_code)
            else:
                none_proc += 1
        inff.close()

        print("\tNone Proc Code: ", none_proc)
        print('')
        return self.mimic_data

    def process_lab_event(self, infile):
        print("processing lab event table...")
        inff = open(infile, 'r')
        count = 0

        for line in csv.DictReader(inff):
            count += 1
            if count % 10000 == 0:
                print("\r\tcount: {}/{}".format(count, 27854055), end='')

            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            charttime = datetime.strptime(line['CHARTTIME'], "%Y-%m-%d %H:%M:%S")
            item_id = line['ITEMID']
            flag = "normal" if line['FLAG'] in ['', None, np.nan] else "abnormal"

            try:
                hadm_obj = self.mimic_data[patient_id]['admissions'][hadm_id]
            except KeyError:                 # only lab test case
                patient_obj = self.mimic_data[patient_id]

                cnt = 1
                for adm_id, adm_obj in patient_obj['admissions'].items():
                    if adm_id.startswith("visit_"):
                        if charttime not in adm_obj.labevent_list.elements:         # 다른 visit
                            cnt += 1
                        else:
                            hadm_id = adm_id
                            break

                if hadm_id not in patient_obj['admissions']:
                    hadm_id = "visit_{}".format(cnt)
                    hadm_obj = HospitalEncounter(
                        patient_obj=patient_obj,
                        hadm_id=hadm_id,
                        admit_time=charttime,
                        disch_time=charttime,
                        is_for_blood_test=1
                    )
                    self.mimic_data[patient_id]['admissions'][hadm_id] = hadm_obj
                else:
                    hadm_obj = patient_obj['admissions'][hadm_id]

            if hadm_obj.labevent_list is None:
                self.mimic_data[patient_id]['admissions'][hadm_id].labevent_list = LabEvent(hadm_id)

            lab_result = (charttime, item_id, flag)
            self.mimic_data[patient_id]['admissions'][hadm_id].labevent_list.add_element(lab_result)

        inff.close()
        print('')
        return self.mimic_data

    def _sort_admissions(self):

        print("Sorting patient dict by 'admit time'....", end=' ')
        for patient_id in self.mimic_data.keys():
            patient_info = self.mimic_data[patient_id]

            # sorting results: [(hadm_id1, hadm_obj1), (hadm_id2, hadm_obj2), ...]
            temp_list = sorted(patient_info['admissions'].items(),
                               key=lambda x: x[1].admit_time)       # current 'List' type
            sorted_dict = {}
            cnt = 1
            for hadm_id, hadm_obj in temp_list:
                if hadm_id.startswith('visit'):
                    modified_hadm_id = "visit_{}".format(cnt)
                    cnt += 1
                else:
                    modified_hadm_id = hadm_id

                sorted_dict[modified_hadm_id] = hadm_obj

            sorted_dict = list(sorted_dict.items())                         # current 'List' type
            if len(sorted_dict) >= 2:
                for hadm_obj in sorted_dict[1:]:
                    hadm_obj[1].readmission = 1
            last_admit = sorted_dict[-1][1]

            self.mimic_data[patient_id]['patient'].ethnicity = last_admit.hadm_ethnicity             # 가장 마지막 방문 때의 종교
            self.mimic_data[patient_id]['patient'].insurance = last_admit.hadm_insurance             # 가장 마지막 방문 때의 보험 여부
            self.mimic_data[patient_id]['patient'].marital_status = last_admit.hadm_marital_status   # 가장 마지막 방문 때의 결혼 여부
            self.mimic_data[patient_id]['patient'].age = last_admit.hadm_age
            self.mimic_data[patient_id]['admissions'] = dict(sorted_dict)                 # change the list to 'dict' type

        print("Done!")

    def _sort_lab_events(self):
        print("Sorting lab results...", end=' ')
        for patient_id, patient_obj in self.mimic_data.items():
            admissions = patient_obj['admissions']
            for (hadm_id, hadm_obj) in admissions.items():
                if hadm_obj.labevent_list is not None:
                    lab_result_dict = dict(sorted(hadm_obj.labevent_list.elements.items(), key=lambda x: x[0]))
                    self.mimic_data[patient_id]['admissions'][hadm_id].labevent_list.elements = lab_result_dict

        print('Done!')

    def load_data(self, data_path='./data/mimic/mimic-iii'):
        data = os.path.join(data_path, 'patientInfo_mimic3')

        if os.path.exists(data):
            self.mimic_data = load_file(data)
        else:
            patient_file = os.path.join(data_path, 'PATIENTS.csv')
            admission_file = os.path.join(data_path, 'ADMISSIONS.csv')
            diagnosis_file = os.path.join(data_path, 'DIAGNOSES_ICD.csv')
            prescriptions_file = os.path.join(data_path, 'PRESCRIPTIONS.csv')
            procedure_file = os.path.join(data_path, 'PROCEDURES_ICD.csv')
            labevent_file = os.path.join(data_path, 'LABEVENTS.csv')

            self.mimic_data = self.process_patient(patient_file)
            self.mimic_data = self.process_admission(admission_file)

            self.mimic_data = self.process_dx_icd(diagnosis_file)
            self.mimic_data = self.process_rx(prescriptions_file)
            self.mimic_data = self.process_proc(procedure_file)
            self.mimic_data = self.process_lab_event(labevent_file)
            self._sort_admissions()
            self._sort_lab_events()

        return self.mimic_data

    def get_number_expired_patients(self):
        pass

    def get_readmission_patients(self, min_visit=1):
        if len(self.mimic_data) < 1:
            raise "No patient data!"
        else:
            target_patients = {}

            for patient_id, patient_obj in self.mimic_data.items():
                admit_dict = self._get_admit_list(patient_id)
                if len(admit_dict) >= min_visit:
                    target_patients[patient_id] = patient_obj
            return target_patients

    def _get_admit_list(self, patient_id):
        admit_dict = self.mimic_data[patient_id]['admissions']
        admit_list = [(hadm_id, hadm_obj) for (hadm_id, hadm_obj) in admit_dict.items() if not hadm_id.startswith('visit')]
        return admit_list


if __name__ == '__main__':
    pass

# from mimic_iii.dataset import *; mimic = MIMICDataset(version=9); patient_dict = mimic.load_data();
