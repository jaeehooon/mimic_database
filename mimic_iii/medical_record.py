class Record(object):
    def __init__(self, hadm_id):
        self.hadm_id = hadm_id
        self.elements = []

    def get_number_elements(self):
        return len(self.elements)

    def get_hadm_id(self):
        return self.hadm_id


class DxRecord(Record):
    def __init__(self, hadm_id, icd_version):
        super().__init__(hadm_id)
        self.version = icd_version

    def add_element(self, item):
        """
        This method is for adding 'Dx' item from 'diagnoses_icd.csv' table to this instance
            'item' is for ICD code

        Args:
            item:       dx code
        """
        self.elements.append(item)

    # @staticmethod
    # def convert_to_icd9(dxStr):
    #     if dxStr.startswith('E'):
    #         if len(dxStr) > 4:
    #             return dxStr[:4] + '.' + dxStr[4:]
    #         else:
    #             return dxStr
    #     else:
    #         if len(dxStr) > 3:
    #             return dxStr[:3] + '.' + dxStr[3:]
    #         else:
    #             return dxStr
    #
    # @staticmethod
    # def convert_to_3digit_icd9(dxStr):
    #     if dxStr.startswith('E'):
    #         if len(dxStr) > 4:
    #             return dxStr[:4]
    #         else:
    #             return dxStr
    #     else:
    #         if len(dxStr) > 3:
    #             return dxStr[:3]
    #         else:
    #             return dxStr

    # def get_3digit_code(self):
    #     result_list = [self.convert_to_3digit_icd9(item) for item in self.elements]
    #     return result_list


class DRGRecord(Record):
    def __init__(self, hadm_id):
        super().__init__(hadm_id)

    def add_element(self, item):
        """
        This method is for adding 'DRG Code' item from 'drgcodes.csv' table to this instance
            'item' is for DRG code

        Args:
            item:
        """


class RxRecord(Record):
    def __init__(self, hadm_id):
        super().__init__(hadm_id)

    def add_element(self, item):
        """

        Args:
            item:
        """
        self.elements.append(item)


class ProcRecord(Record):
    def __init__(self, hadm_id, icd_version):
        super().__init__(hadm_id)
        self.version = icd_version

    def add_element(self, item):
        """

        Args:
            item:
        """
        self.elements.append(item)


class LabEvent(Record):
    def __init__(self, hadm_id):
        super().__init__(hadm_id)
        self.elements = {}              # overriding

    def add_element(self, item):
        """

        Args
            item:           (charttime, item, flag)
        """
        (chart_time, item_id, flag) = item
        if chart_time not in self.elements:
            self.elements[chart_time] = []
        self.elements[chart_time].append((item_id, flag))

    def get_number_elements(self):
        element_list = [elements[0] for elements in self.elements.values()]
        return len(element_list)