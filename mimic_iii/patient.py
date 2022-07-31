"""


"""


def patient(subject_id, dob=None, dod=None, gender=None, expired=None):
    """
    This method is for a patient.
        A patient's attribute is derived from 'PATIENTS.csv', 'ADMISSIONS.csv' Table
        Especially, [ethnicity, marital_status, insurance, language] data is from 'the last admission'
    """
    patient_info = {
        'subject_id': subject_id,
        'gender': gender,
        'dob': dob,
        'dod': dod,
        'expired': expired
    }
    return patient_info
