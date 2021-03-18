import xml.etree.ElementTree as xmlet
from pathlib import Path
import numpy as np

from craamvert.instruments import XML_TYPE_TO_NUMPY_TYPE, CASLEO, GMT_NEGATIVE_3
from instruments.utils.hdu_handlers import create_primary_hdu
from craamvert.instruments.sst import SST_FULL_NAME, SST_LATITUDE_LONGITUDE_HEIGHT, SST_RBD, SST_FREQUENCY
from craamvert.utils import INVALID_FILE_NAME, iso_time, RBD_TYPE

MAP_RBD_TYPE = {
    "RS": "Integration",
    "RF": "Subintegration",
    "BI": "Auxiliary"
}
MAP_RBD_TYPE_TO_FILE_TYPE = {
    "Integration": "Data",
    "Subintegration": "Data",
    "Auxiliary": "Auxiliary"
}


class RBD:

    def __init__(self):
        # All attributes must be declared on __init__

        # RBD information
        self.date = None
        self.time = None
        self.start_time = None
        self.end_time = None

        # RBD Data
        self.column_names = None
        self.data = None

        self.__rbd_type = None

        # Fits information
        self.primary_hdu = None

    def convert_from_file(self, path, file_name, path_to_xml):
        """Loads data from a file and returns an `SST` object.

        Parameters:
                path : pathlib.Path - Location of the SST file in the file system.
                file_name : str - Name of the SST file.
                path_to_xml : Path, optional - Location of the SST xml description files in the file system.

        Raises:
                ValueError: If the filename is invalid.
        """

        # Match prefix to RBD type
        type_prefix = file_name[:2].upper()
        self.__rbd_type = MAP_RBD_TYPE[type_prefix]

        # Get date from file name
        file_name_date = file_name[2:].split(".")

        if len(file_name_date[0]) == 6:
            self.date = str(int(file_name_date[0][:2]) + 1900) + '-' + file_name_date[0][2:4] + '-' + file_name_date[
                                                                                                            0][4:6]
        elif len(file_name_date[0]) == 7:
            self.date = str(int(file_name_date[0][:3]) + 1900) + '-' + file_name_date[0][3:5] + '-' + file_name_date[
                                                                                                            0][5:7]
        else:
            raise ValueError(INVALID_FILE_NAME.format(file_name))

        # Get time from file name
        self.time = "00:00"
        if len(file_name_date) > 1:
            self.time = file_name_date[1][:2] + ":" + file_name_date[1][2:4]

        # Extract values equivalent to RBD column names
        self.column_names = self.__get_column_names(path_to_xml)

        rbd_column_names_list = list()
        for key, value in self.column_names.items():
            rbd_column_names_list.append((key, value[1], value[0]))

        # Extract values equivalent to RBD data
        if isinstance(path, bytes):
            self.data = np.frombuffer(path, dtype=rbd_column_names_list)
        else:
            self.data = np.fromfile(str(path), dtype=rbd_column_names_list)

        # Get time span of data
        self.start_time, self.end_time = self.__get_time_span()

        # Create fits Primary Header Data Unit (HDU)
        self.primary_hdu = create_primary_hdu(self.date,
                                         self.start_time,
                                         self.end_time,
                                         SST_FULL_NAME,
                                         SST_LATITUDE_LONGITUDE_HEIGHT,
                                         CASLEO,
                                         GMT_NEGATIVE_3,
                                         RBD_TYPE,
                                         file_name,
                                         SST_RBD,
                                         SST_FREQUENCY)

        self.start_time = self.start_time[:8]
        self.end_time = self.end_time[:8]

        return self

        # -------------------------------------------------------------
        #                      PRIVATE FUNCTIONS
        #             always use __ before function name
        # -------------------------------------------------------------

    def __get_column_names(self, path_to_xml):
        """
        Method for finding the correct description file.
        Returns a dict representing the description found,
        the key is the variable name and the value is a list
        containing the var dimension, type and unit respectively.
        """
        span_table = xmlet.parse(path_to_xml / Path("SSTDataFormatTimeSpanTable.xml")).getroot()
        filetype = MAP_RBD_TYPE_TO_FILE_TYPE[self.__rbd_type]

        for item in span_table:
            if item[0].text == filetype and item[1].text <= self.date <= item[2].text:
                data_description_file_name = item[3].text

        xml = xmlet.parse(path_to_xml / Path(data_description_file_name)).getroot()

        header = dict()
        for child in xml:
            var_name = child[0].text
            var_dim = int(child[1].text)
            var_type = child[2].text
            var_unit = child[3].text

            np_type = XML_TYPE_TO_NUMPY_TYPE[var_type]

            header.update({var_name: [var_dim, np_type, var_unit]})

        return header

    def __get_time_span(self):
        """
        Returns ISO time of the first and last record found in the data.
        """

        nonzero = self.data["time"].nonzero()
        return iso_time.time(self.data["time"][nonzero[0][0]]), iso_time.time(
            self.data["time"][nonzero[0][-1]])
