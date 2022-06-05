import sys


class ICDCodeConverter(object):

    def __init__(self, path='./data/mapping_table/'):
        self.path = path
        self.icd9_to_icd10, self.icd10_to_icd9 = self.load_file()

    def load_file(self):
        """
        This method is for loading file.
            and this method references basically this link as follow,
            1. https://github.com/MIT-LCP/mimic-code/issues/931
            2. https://www.cms.gov/Medicare/Coding/ICD10/2018-ICD-10-CM-and-GEMs
            3. https://github.com/ZhiGroup/terminology_representation

        Return:
            two dictionaries for ICD codes
        """
        icd9_to_10, icd10_to_9 = {}, {}

        # ICD9CM to ICD10CM
        with open(self.path + '2018_I9gem.txt', 'r') as f:
            lines = f.readlines()

            for line in lines:
                icd9cm, icd10cm, _ = line.split()
                try:
                    if icd10cm not in icd9_to_10[icd9cm]:
                        icd9_to_10[icd9cm].append(icd10cm)
                except KeyError:
                    icd9_to_10[icd9cm] = [icd10cm]

        with open(self.path + 'rawICD9_to_ICD10.txt', 'r') as f:
            lines = f.readlines()

            for line in lines[1:]:
                elements = line.split('\t')
                dx_code, icd9cm, icd10cm = elements[1], elements[-3], elements[-2]

                if icd9cm.startswith('NKP'):
                    continue

                icd9cm = dx_code.replace('.', '')
                try:
                    if icd10cm not in icd9_to_10[icd9cm]:
                        icd9_to_10[icd9cm].append(icd10cm)
                except KeyError:
                    icd9_to_10[icd9cm] = [icd10cm]
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

        # ICD10CM to ICD9CM
        with open(self.path + '2018_I10gem.txt', 'r') as f:
            lines = f.readlines()

            for line in lines:
                icd10cm, icd9cm, _ = line.split()
                try:
                    if icd9cm not in icd10_to_9[icd10cm]:
                        icd10_to_9[icd10cm].append(icd9cm)
                except KeyError:
                    icd10_to_9[icd10cm] = [icd9cm]

        with open(self.path + 'rawICD10_to_ICD9.txt', 'r') as f:
            lines = f.readlines()

            for line in lines[1:]:
                elements = line.split('\t')
                dx_code, icd9cm, icd10cm = elements[1], elements[-3], elements[-2]

                icd10cm = dx_code.replace('.', '')
                try:
                    if icd9cm not in icd10_to_9[icd10cm]:
                        icd10_to_9[icd10cm].append(icd9cm)
                except KeyError:
                    icd10_to_9[icd10cm] = [icd9cm]

        return icd9_to_10, icd10_to_9

    def convert(self, src, version='9'):
        """
        1. This methods is for converting ICD9CM to ICD10CM or
            ICD10CM to ICD9CM.
        2. There are some codes that have many mappings,
            so, we just pick the first index mapped code.
            e.g.
                ICD9CM : 00589
                ICD10CM: ['A054', 'A058']
                We pick 'A054'
        3. If you want to convert 'ICD10CM to ICD9CM',
            there are some codes that can't be converted to ICD9CM,
            e.g. 'T84048A', 'C441122', 'F530', ...
                In MIMIC-IV,
                    no mapping:                         3,445
                    ICD 10 code in 'diagnoses_icd.csv': 2,189,981
                    total code:                         5,280,351
            There's no mapping code to them,
                so it has to be excluded when you do this.


        Args:
            src:            the code to be converted
            version:        the version to be converted
        Return:
            if src is ICD9CM and version '10',
                it will return ICD10CM,
            or src is ICD10CM and version '9',
                it will return ICD9CM.
        """
        try:
            if version == '9':
                return self.icd9_to_icd10[src][0]
            elif version == '10':
                return self.icd10_to_icd9[src][0]
        except KeyError:
            return None
