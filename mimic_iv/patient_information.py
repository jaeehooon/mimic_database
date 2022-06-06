"""

"""


class Patient(object):
    def __init__(self, subject_id, gender=None, anchor_age=None, anchor_year=None):
        self.subject_id = subject_id                        # Patient ID
        self.dob = None                                     # patient's the date of birth
        self.dod = None                                     # patient's the date of death
        self.gender = gender                                # gender
        self.expired = None                                 # whether expired or not 'now'
        self.age = None                                     # age
        self.marital_status = None                          # whether maried or not from the last encounter(visit)
        self.ethnicity = None                               # ethnicity
        self.insurance = None                               # insurance
        self.expired = None                                 # expired
        self.is_organ_donor = False                         # Is Organ Donor or not

        self.anchor_age = anchor_age
        self.anchor_year = anchor_year
        self.admit_dict = {}

    def get_admit_list(self):
        pass

    def print_info(self):
        print("####################")
        print("Patient ID: ", self.subject_id)
        print("\tDOB: ", self.dob)
        print("\tDOD: ", self.dod)
        print('\tAGE: ', self.age)
        print("\tExpired: ", self.expired)
        print("\tGender: ", self.gender)
        print("\tMarital Status: ", self.marital_status)
        print("\tEthnicity: ", self.ethnicity)
        print("\tInsurance: ", self.insurance)
        print("\tOrgan Donor: ", 'Yes' if self.is_organ_donor else 'No')
        print("\t# of visits: ", len(self.admit_dict))
        print("####################")


class EncounterInfo(object):
    def __init__(self, patient_obj, hadm_id, is_for_blood_test=0, age=None,
                 admit_dx=None, admit_time=None, disch_time=None, death_time=None,
                 admit_type=None, admit_loc=None, disch_loc=None,
                 marital_status=None, ethnicity=None, insurance=None, language=None,
                 expired=None, hospital_expire_flag=None, is_organ_donor=False):

        self.patient_obj = patient_obj
        self.hadm_id = hadm_id
        self.is_for_blood_test = is_for_blood_test                  # Is only admission for 'blood test' (Lab Result)
        self.admit_dx = admit_dx                                    # Hospital Admission Diagnosis
        self.admit_time = admit_time                                # Hospital Admission Time
        self.disch_time = disch_time                                # Hospital Discharge Time
        self.death_time = death_time
        self.admit_type = admit_type                                # Admission Type
        self.admit_loc = admit_loc                                  # Admission Location
        self.disch_loc = disch_loc                                  # Discharge Location
        self.los = (((disch_time - admit_time).days * 24 * 60 * 60) +
                    (disch_time - admit_time).seconds) / 60 / 60    # LOS (hours)
        self.hadm_age = age                                         # age when a patient visits
        self.marital_status = marital_status                        # Marital Status
        self.ethnicity = ethnicity                                  # Ethnicity
        self.insurance = insurance                                  # Insurance
        self.language = language                                    # Language

        self.readmission = 0                                        # This visit is whether re-admission or not
        self.expired = expired                                      # expired
        self.hospital_expire_flag = hospital_expire_flag            # Whether the patient's expired in the visit
        self.is_organ_donor = is_organ_donor

        # records
        self.dx_list = None
        self.drg_list = None
        self.rx_list = None
        self.proc_list = None
        self.labevent_list = None

    def update(self):
        """
        This method is for patient's demographic information as 'patient' level
        The last visit's demographic information of patient represent patient one,
            and this is going to be used for only the last visit.
        """
        self.patient_obj.age = self.hadm_age
        self.patient_obj.marital_status = self.marital_status
        self.patient_obj.ethnicity = self.ethnicity
        self.patient_obj.insurance = self.insurance
        self.patient_obj.language = self.language
        self.is_organ_donor = self.is_organ_donor

    def print_info(self, patient_info=True):
        if patient_info:
            self.patient_obj.print_info()
        print('\n')
        print("HADM_ID: ", self.hadm_id)
        print("IS FOR BLOOD TEST: ", self.is_for_blood_test)
        print("Admit Dx: ", self.admit_dx)
        print("Admit Time: ", self.admit_time)
        print("Disch Time: ", self.disch_time)
        print("Admit Type: ", self.admit_type)
        print("Admit Loc: ", self.admit_loc)
        print("Disch Loc: ", self.disch_loc)
        print("HADM Age: ", self.hadm_age)
        print("LOS: ", self.los)

        print("Readmission: ", self.readmission)
        print("Expired: ", self.expired)
        print("Hospital Expire Flag: ", self.hospital_expire_flag)

        print()
        print("# of Dx Code: ", self.dx_list.get_number_elements())
        print("\tDx: ", self.dx_list.elements)
        print('# of DRG Code: ', self.drg_list.get_number_elements())
        print("\tDRG: ", self.drg_list.elements)


class Record(object):
    def __init__(self, hadm_id):
        self.hadm_id = hadm_id
        self.elements = []

    def get_number_elements(self):
        return len(self.elements)

    def get_hadm_id(self):
        return self.hadm_id


class DxRecord(Record):
    def __init__(self, hadm_id, version):
        super().__init__(hadm_id)
        self.version = version

    def add_element(self, item):
        """
        This method is for adding 'Dx' item from 'diagnoses_icd.csv' table to this instance
            'item' is for ICD code

        Args:
            item:       dx code
        """
        self.elements.append(item)


class DRGRecord(Record):
    def __init__(self, hadm_id):
        super().__init__(hadm_id)

    def add_element(self, item):
        """
        This method is for adding 'DRG Code' item from 'drgcodes.csv' table to this instance
            'item' is for DRG code

        Args:
            item:       [drg code, drg_type]
        """
        drg_type, drg_code = item
        drg_code = "{}_{}".format(drg_type, drg_code)
        self.elements.append(drg_code)


class RxRecord(Record):
    def __init__(self, hadm_id):
        super().__init__(hadm_id)

    def add_elements(self, item):
        """

        Args:
            item:       [drug, drug_type, ndc]
        """
        self.elements.append(item)


class ICUEncounterInfo(object):
    def __init__(self, icu_stay_id, hadm_id, subject_id):
        super().__init__(hadm_id, subject_id)
        self.icu_stay_id = icu_stay_id

