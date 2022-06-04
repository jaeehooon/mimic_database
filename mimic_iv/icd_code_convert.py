import sys


class ICDCodeConverter(object):

    def __init__(self, path='./data/mapping_table/'):
        self.path = path
        self.icd9_to_icd10, self.icd10_to_icd9 = None, None

    def load_file(self):
        """
        This method is for loading file.
            and this method references basically this link as follow,
            1. https://github.com/MIT-LCP/mimic-code/issues/931
            2. https://www.cms.gov/Medicare/Coding/ICD10/2018-ICD-10-CM-and-GEMs

        Return:
            two dictionaries for ICD codes
        """
        icd9_to_10, icd10_to_9 = {}, {}
        with open(self.path + '2018_I9gem.txt', 'r') as f:
            lines = f.readlines()

            for line in lines:
                icd9cm, icd10cm, _ = line.split()
                if icd9cm not in icd9_to_10:
                    icd9_to_10[icd9cm] = []
                icd9_to_10[icd9cm].append(icd10cm)

        with open(self.path + '2018_I10gem.txt', 'r') as f:
            lines = f.readlines()

            for line in lines:
                icd10cm, icd9cm, _ = line.split()
                if icd10cm not in icd10_to_9:
                    icd10_to_9[icd10cm] = []
                icd10_to_9[icd10cm].append(icd9cm)

        with open(self.path + 'rawICD9_to_ICD10.txt', 'r') as f:
            lines = f.readlines()

            for line in lines[1:]:
                elements = line.split('\t')
                dx_code, icd9cm, icd10cm = elements[1], elements[-3], elements[-2]

                if icd9cm.startswith('NKP'):
                    continue

                icd9cm = dx_code.replace('.', '')

                if icd9cm not in icd9_to_10:
                    icd9_to_10[icd9cm] = icd10cm

        """
        Injury due to war operations by other and unspecified forms of conventional warfare
        It's the same as the 'E9950' ICD9 code
        """
        icd9_to_10['E995'] = 'Y36440A'

        """
        Necrotizing enterocolitis in newborn, unspecified.
        It's the same for the '77750' ICD9 Code
        """
        icd9_to_10['7775'] = 'P779'

        return icd9_to_10, icd10_to_9
