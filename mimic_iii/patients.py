"""


"""


class Patient(object):

    def __init__(self, subject_id, dob=None, dod=None, gender=None, expired=None):
        self.subject_id = subject_id
        self.dob = dob                                     # patient's the date of birth
        self.dod = dod                                     # patient's the date of death
        self.gender = gender                               # gender
        self.age = None                                    # age
        self.marital_status = None                         # whether maried or not from the last encounter(visit)
        self.ethnicity = None                              # ethnicity
        self.insurance = None                              # insurance
        self.language = None                               # language
        self.expired = expired                             # expired

        # self.admit_dict = {}
        self.total_stays = 0                               # total hospitalization stay
