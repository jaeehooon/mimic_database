import sys
import os
import pickle
import csv
import numpy as np
sys.path.append(os.pardir)
from datetime import datetime
from tqdm.auto import tqdm

from patient import patient
from medical_codes import *
from encounters import hospital_encounter
# from utils.convert import ICDCodeConverter
from utils.demographic_processing import *
from utils.utils import *


class MIMICDataset(object):

    def __init__(self, version):
        self.mimic_data = {}
        self.icd_version = version                                  # ICD Code version
        # self.icd_converter = ICDCodeConverter()

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
                'patient': patient(
                    subject_id=patient_id,
                    dob=dob,
                    dod=dod,
                    gender=gender,
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
                patient_obj = patient(subject_id=patient_id)
                self.mimic_data[patient_id] = {
                    'patient': patient_obj,
                    'admissions': {},
                    'icu_stays': {}
                }
            patient_obj = self.mimic_data[patient_id]['patient']

            hadm_id = line['HADM_ID']
            admit_dx = None
            admit_time = datetime.strptime(line['ADMITTIME'], "%Y-%m-%d %H:%M:%S")
            disch_time = datetime.strptime(line['DISCHTIME'], "%Y-%m-%d %H:%M:%S")
            death_time = datetime.strptime(line['DEATHTIME'], "%Y-%m-%d %H:%M:%S") \
                if line['DEATHTIME'] not in [np.nan, None, ''] else np.nan

            admit_type = line['ADMISSION_TYPE']
            admit_loc = line['ADMISSION_LOCATION']
            disch_loc = line['DISCHARGE_LOCATION']
            ethnicity = process_ethnicity(line['ETHNICITY'])
            insurance = line['INSURANCE']
            marital_status = process_marital(line['MARITAL_STATUS'])
            expired = line['HOSPITAL_EXPIRE_FLAG']
            has_chartevents = line['HAS_CHARTEVENTS_DATA']

            hadm_age = int(round((admit_time - patient_obj['dob']).days / 365))
            """
            NEWBORN ??? admit_type??? ??????:       7,864
            ????????? 0?????? ??????:                    7,874
            """
            hadm_obj = hospital_encounter(
                patient_obj=patient_obj,
                hadm_id=hadm_id,
                is_for_blood_test=0,
                admit_dx=admit_dx,
                admit_time=admit_time,
                disch_time=disch_time,
                death_time=death_time,
                admit_type=admit_type,
                admit_loc=admit_loc,
                disch_loc=disch_loc,
                age=hadm_age,                           # age when a patient visits
                marital_status=marital_status,          # Marital Status
                ethnicity=ethnicity,                    # Ethnicity
                insurance=insurance,                    # Insurance
                language=None,                          # Language
                hospital_expire_flag=expired,           # flag whether the patient died 'in the hospital'
                has_chartevents=has_chartevents
            )

            self.mimic_data[patient_id]['admissions'][hadm_id] = hadm_obj
            # self.mimic_data[patient_id]['patient'].total_stays += hadm_obj.los
            count += 1

        inff.close()
        print('')
        return self.mimic_data

    def process_dx_icd(self, infile):
        print("processing diagnosis_icd table....")
        none_dx = 0
        excluded_count = 0
        inff = open(infile, 'r')
        for line in csv.DictReader(inff):
            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            icd_code = line['ICD9_CODE']

            if patient_id not in self.mimic_data:
                self.mimic_data[patient_id] = {
                    'patient': patient(subject_id=patient_id),
                    'admissions': {},
                    'icu_stays': {}
                }
            patient_obj = self.mimic_data[patient_id]

            if hadm_id not in patient_obj['admissions']:
                excluded_count += 1
                continue
            hadm_obj = patient_obj['admissions'][hadm_id]

            if hadm_obj['dx_list'] is None:
                self.mimic_data[patient_id]['admissions'][hadm_id]['dx_list'] = dx_record(
                    hadm_id=hadm_id,
                    icd_version=self.icd_version
                )
            dx_list = hadm_obj['dx_list']

            # icd_code = self.icd_converter.convert_dx_digit()
            if icd_code not in ['', np.nan, None]:
                dx_list = add_element(dx_list, icd_code, 'dx')
            else:
                none_dx += 1

            hadm_obj['dx_list'] = dx_list
            self.mimic_data[patient_id]['admissions'][hadm_id] = hadm_obj

        inff.close()
        print('\tNone Dx Code: ', none_dx)
        print(f"\t# of excluded HADM_ID: {excluded_count}")
        print('')
        return self.mimic_data

    def process_rx(self, infile):
        print("processing prescriptions table...")
        excluded_count = 0
        count = 0
        inff = open(infile, 'r')
        for line in csv.DictReader(inff):
            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            count += 1

            if count % 10000 == 0 or count == 4156450:
                print("\r\tcount: {:,d}/{:,d}".format(count, 4156450), end='')

            if patient_id not in self.mimic_data:
                self.mimic_data[patient_id] = {
                    'patient': patient(subject_id=patient_id),
                    'admissions': {},
                    'icu_stays': {}
                }
            patient_obj = self.mimic_data[patient_id]

            if hadm_id not in patient_obj['admissions']:
                excluded_count += 1
                continue
            hadm_obj = patient_obj['admissions'][hadm_id]

            if hadm_obj['rx_list'] is None:
                hadm_obj['rx_list'] = rx_record(hadm_id)
            rx_list = hadm_obj['rx_list']

            drug = line['DRUG']
            fdc = line['FORMULARY_DRUG_CD']
            drug_type = line['DRUG_TYPE']
            route = line['ROUTE']
            item = (drug, fdc, drug_type, route)

            rx_list = add_element(rx_list, item, 'rx')
            hadm_obj['rx_list'] = rx_list
            self.mimic_data[patient_id]['admissions'][hadm_id] = hadm_obj

        inff.close()
        print("\n\t# of excluded HADM_ID: {:,d}".format(excluded_count))
        # print('\t# of Rx Code including None: ', none_rx)
        print('')

        return self.mimic_data

    def process_proc(self, infile):

        print("processing procedure table....")
        none_proc = 0
        excluded_count = 0
        inff = open(infile, 'r')
        for line in csv.DictReader(inff):
            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            icd_code = line['ICD9_CODE']

            if patient_id not in self.mimic_data:
                self.mimic_data[patient_id] = {
                    'patient': patient(subject_id=patient_id),
                    'admissions': {},
                    'icu_stays': {}
                }
            patient_obj = self.mimic_data[patient_id]

            if hadm_id not in patient_obj['admissions']:
                excluded_count += 1
                continue
            hadm_obj = patient_obj['admissions'][hadm_id]

            if hadm_obj['proc_list'] is None:
                self.mimic_data[patient_id]['admissions'][hadm_id]['proc_list'] = proc_record(
                    hadm_id=hadm_id,
                    icd_version=self.icd_version
                )
            proc_list = hadm_obj['proc_list']

            # icd_code = self.icd_converter.convert_proc_digit(line['ICD9_CODE'])
            if icd_code not in ['', np.nan, None]:
                proc_list = add_element(proc_list, icd_code, 'proc')
            else:
                none_proc += 1

            hadm_obj['proc_list'] = proc_list
            self.mimic_data[patient_id]['admissions'][hadm_id] = hadm_obj

        inff.close()

        print("\tNone Proc Code: ", none_proc)
        print(f"\t# of excluded HADM_ID: {excluded_count}")
        print('')
        return self.mimic_data

    def process_lab_event(self, infile):
        print("processing lab event table...")
        inff = open(infile, 'r')
        count = 0
        excluded_count = 0
        for line in csv.DictReader(inff):
            count += 1

            if count % 10000 == 0 or count == 27854055:
                print("\r\tcount: {:,d}/{:,d}".format(count, 27854055), end='')

            patient_id = line['SUBJECT_ID']
            hadm_id = line['HADM_ID']
            charttime = datetime.strptime(line['CHARTTIME'], "%Y-%m-%d %H:%M:%S")
            item_id = line['ITEMID']
            flag = "normal" if line['FLAG'] in ['', None, np.nan] else "abnormal"

            if patient_id not in self.mimic_data:
                self.mimic_data[patient_id] = {
                    'patient': patient(subject_id=patient_id),
                    'admissions': {},
                    'icu_stays': {}
                }
            patient_obj = self.mimic_data[patient_id]

            if hadm_id not in patient_obj['admissions']:
                excluded_count += 1
                continue
            hadm_obj = patient_obj['admissions'][hadm_id]

            if hadm_obj['lab_list'] is None:
                hadm_obj['lab_list'] = lab_record(hadm_id)
            lab_list = hadm_obj['lab_list']

            lab_result = (charttime, item_id, flag)
            lab_list = add_element(lab_list, lab_result, 'lab')

            hadm_obj['lab_list'] = lab_list
            self.mimic_data[patient_id]['admissions'][hadm_id] = hadm_obj

        inff.close()
        print('')
        print(f"\t# of excluded HADM_ID: {excluded_count}")
        return self.mimic_data

    def _sort_admissions(self):

        print("Sorting patient dict by 'admit time'....", end=' ')
        for patient_id in self.mimic_data.keys():
            patient_info = self.mimic_data[patient_id]

            # sorting results: [(hadm_id1, hadm_obj1), (hadm_id2, hadm_obj2), ...]
            temp_list = sorted(patient_info['admissions'].items(),
                               key=lambda x: x[1]['admit_time'])

            if len(temp_list) >= 2:
                for hadm_obj in temp_list[1:]:
                    hadm_obj[1]['readmission'] = 1

            last_hadm_id, last_admit_obj = temp_list[-1]
            self.mimic_data[patient_id]['patient']['ethnicity'] = last_admit_obj['hadm_ethnicity']  # ?????? ????????? ?????? ?????? ??????
            self.mimic_data[patient_id]['patient']['insurance'] = last_admit_obj['hadm_insurance']  # ?????? ????????? ?????? ?????? ?????? ??????
            self.mimic_data[patient_id]['patient']['marital_status'] = last_admit_obj['hadm_marital_status']  # ?????? ????????? ?????? ?????? ?????? ??????
            self.mimic_data[patient_id]['patient']['age'] = last_admit_obj['hadm_age']
            self.mimic_data[patient_id]['admissions'] = dict(temp_list)  # change the list to 'dict' type

        print("Done!")

    def _sort_lab_events(self):
        print("Sorting lab results...", end=' ')
        for patient_id, patient_obj in self.mimic_data.items():
            admissions = patient_obj['admissions']
            for (hadm_id, hadm_obj) in admissions.items():
                if hadm_obj['lab_list'] is not None:
                    lab_result_dict = dict(sorted(hadm_obj['lab_list']['elements'].items(), key=lambda x: x[0]))
                    self.mimic_data[patient_id]['admissions'][hadm_id]['lab_list']['elements'] = lab_result_dict

        print('Done!')

    def load_data(self, data_path='../data/mimic/mimic-iii/'):
        patient_info_file = os.path.join('./', 'patientInfo_mimic3')

        if os.path.exists(patient_info_file):
            self.mimic_data = load_data(patient_info_file)
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


def main(config=None):
    mimic = MIMICDataset(version=9)
    patient_dict = mimic.load_data()
    file_save = True
    if file_save:
        output_path = './patientInfo_mimic3'
        save_data(output_path, patient_dict)


if __name__ == '__main__':
    main()

# from mimic_iii.dataset import *; mimic = MIMICDataset(version=9); patient_dict = mimic.load_data();
