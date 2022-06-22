import csv
import sys
import json


class ICDCodeConverter(object):

    def __init__(self, path='./data/mapping_table/'):
        self.path = path
        self.icd9_to_icd10cm, self.icd10_to_icd9cm, self.icd9_to_icd10pcs, self.icd10_to_icd9pcs = self.load_file()

    def get_converter_mapping(self):
        return self.icd9_to_icd10cm, self.icd10_to_icd9cm, self.icd9_to_icd10pcs, self.icd10_to_icd9pcs

    def load_file(self):
        """
        This method is for loading file.
            and this method references basically this link as follow,
            1. https://github.com/MIT-LCP/mimic-code/issues/931
            2. https://www.cms.gov/Medicare/Coding/ICD10/2018-ICD-10-CM-and-GEMs
            3. https://github.com/ZhiGroup/terminology_representation
            4. https://www.nber.org/research/data/icd-9-cm-and-icd-10-cm-and-icd-10-pcs-crosswalk-or-general-equivalence-mappings

        Return:
            two dictionaries for ICD codes
        """
        icd9_to_10cm, icd10_to_9cm = {}, {}
        icd9_to_10pcs, icd10_to_9pcs = {}, {}

        ###########
        # Diagnosis Code
        ###################

        # ICD9CM to ICD10CM
        with open(self.path + '2018_I9gem.txt', 'r') as f:
            lines = f.readlines()

            for line in lines:
                icd9cm, icd10cm, _ = line.split()
                try:
                    if icd10cm not in icd9_to_10cm[icd9cm]:
                        icd9_to_10cm[icd9cm].append(icd10cm)
                except KeyError:
                    icd9_to_10cm[icd9cm] = [icd10cm]

        with open(self.path + 'rawICD9_to_ICD10.txt', 'r') as f:
            lines = f.readlines()

            for line in lines[1:]:
                elements = line.split('\t')
                dx_code, icd9cm, icd10cm = elements[1], elements[-3], elements[-2]

                if icd9cm.startswith('NKP'):
                    continue

                icd9cm = dx_code.replace('.', '')
                try:
                    if icd10cm not in icd9_to_10cm[icd9cm]:
                        icd9_to_10cm[icd9cm].append(icd10cm)
                except KeyError:
                    icd9_to_10cm[icd9cm] = [icd10cm]
        """
        Injury due to war operations by other and unspecified forms of conventional warfare
        It's the same as the 'E9950' ICD9 code
        """
        icd9_to_10cm['E995'] = 'Y36440A'

        """
        Necrotizing enterocolitis in newborn, unspecified.
        It's the same for the '77750' ICD9 Code
        """
        icd9_to_10cm['7775'] = 'P779'

        # ICD10CM to ICD9CM
        with open(self.path + '2018_I10gem.txt', 'r') as f:
            lines = f.readlines()

            for line in lines:
                icd10cm, icd9cm, _ = line.split()
                try:
                    if icd9cm not in icd10_to_9cm[icd10cm]:
                        icd10_to_9cm[icd10cm].append(icd9cm)
                except KeyError:
                    icd10_to_9cm[icd10cm] = [icd9cm]

        with open(self.path + 'rawICD10_to_ICD9.txt', 'r') as f:
            lines = f.readlines()

            for line in lines[1:]:
                elements = line.split('\t')
                dx_code, icd9cm, icd10cm = elements[1], elements[-3], elements[-2]

                icd10cm = dx_code.replace('.', '')
                try:
                    if icd9cm not in icd10_to_9cm[icd10cm]:
                        icd10_to_9cm[icd10cm].append(icd9cm)
                except KeyError:
                    icd10_to_9cm[icd10cm] = [icd9cm]

        ###############
        # for Procedure Code
        ###################
        with open(self.path + 'icd9toicd10pcsgem.csv', 'r') as f:

            for line in csv.DictReader(f):
                icd9pcs = line['icd9cm']
                icd10pcs = line['icd10cm']

                if icd9pcs not in icd9_to_10pcs:
                    icd9_to_10pcs[icd9pcs] = []
                icd9_to_10pcs[icd9pcs].append(icd10pcs)

        with open(self.path + 'icd10pcstoicd9gem.csv', 'r') as f:

            for line in csv.DictReader(f):
                icd9pcs = line['icd9cm']
                icd10pcs = line['icd10cm']

                if icd10pcs not in icd10_to_9pcs:
                    icd10_to_9pcs[icd10pcs] = []
                icd10_to_9pcs[icd10pcs].append(icd9pcs)

        return icd9_to_10cm, icd10_to_9cm, icd9_to_10pcs, icd10_to_9pcs

    def convert_version(self, src, code_type='dx', to_version='10'):
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
            src:                the code to be converted
            code_type:          'Dx' or 'Proc'. default: Dx
            to_version:         the version to be converted
        Return:
            if src is ICD9CM and version '10',
                it will return ICD10CM,
            or src is ICD10CM and version '9',
                it will return ICD9CM.
        """

        if code_type == 'dx':
            return self.convert_dx_code(src, to_version=to_version)
        elif code_type == 'proc':
            return self.convert_proc_code(src, to_version=to_version)
        else:
            raise "Code Error! It has to be 'Dx' or 'Proc'"

    def convert_dx_code(self, src, to_version='10'):
        if to_version == '10':
            try:
                result = self.icd9_to_icd10cm[src][0]
            except KeyError:
                result = None
        elif to_version == '9':
            try:
                result = self.icd10_to_icd9cm[src][0]
                result = self.convert_dx_digit(result)
            except KeyError:
                result = None
        else:
            raise "Version Error!!"
        return result

    def convert_proc_code(self, src, to_version='10'):
        if to_version == '10':
            try:
                result = self.icd9_to_icd10pcs[src][0]
                result = "{}.{}".format(result[:3], result[:3])
            except KeyError:
                result = None
        elif to_version == '9':
            try:
                result = self.icd10_to_icd9pcs[src][0]
                result = "{}.{}".format(result[:3], result[:3])
            except KeyError:
                result = None
        else:
            raise "Version Error!!"
        return result

    @staticmethod
    def convert_dx_digit(src):
        if src.startswith('E'):
            if len(src) > 4:
                result = src[:4] + '.' + src[4:]
            else:
                result = src
        else:
            if len(src) > 3:
                result = src[:3] + '.' + src[3:]
            else:
                result = src

        return result

    @staticmethod
    def convert_proc_digit(src):
        result = None
        if src is not None:
            result = "{:04d}".format(int(src))
            result = "{}.{}".format(result[:2], result[2:])
        return result


class Drug2NDC(object):
    """
    This class is for converting 'Drug' to 'NDC(National Drug Code)'

    https://open.fda.gov/data/downloads/
    """
    def __init__(self, path='./data/mapping_table/'):
        self.path = path
        self.drug_to_ndc = self.load_file()

    def load_file(self):
        drug_to_ndc = {}
        with open(self.path + 'drug-ndc-0001-of-0001.json', 'r') as f:
            drug_ndc = json.load(f)
            for result in drug_ndc['results']:
                try:
                    generic_name = result['generic_name']
                except KeyError:
                    generic_name = result['active_ingredients'][0]['name'].capitalize()

                if generic_name not in drug_to_ndc:
                    drug_to_ndc[generic_name] = result['product_ndc']
        return drug_to_ndc

    def convert(self, item):
        return self.drug_to_ndc[item]
