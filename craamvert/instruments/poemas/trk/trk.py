import xml.etree.ElementTree as xmlet
from pathlib import Path
import collections
import numpy as np

from craamvert.utils import julday, TRK_TYPE, INVALID_XML_FILE
from craamvert.instruments import XML_TYPE_TO_NUMPY_TYPE, CASLEO, GMT_NEGATIVE_3
from instruments.utils.hdu_handlers import create_primary_hdu
from craamvert.instruments.poemas import POEMASDataType, POEMAS_TRK, POEMAS_FULL_NAME, POEMAS_LATITUDE_LONGITUDE_HEIGHT, \
    POEMAS_FREQUENCY

PATH_TO_XML_TRK_COLUMN_NAME = {
    POEMASDataType.HEADER: "POEMASDataFormatHead.xml",
    POEMASDataType.BODY: "POEMASDataFormat.xml",
    POEMASDataType.FULL_BODY: "POEMASFullDataFormat.xml",
}


class TRK:

    def __init__(self):
        # All attributes must be declared on __init__

        # TRK information
        self.date = None
        self.time = None
        self.start_time = None
        self.end_time = None
        self.records = None

        # TRK Header data is equivalent to:
        # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
        self.header_column_names = None
        self.header_data = None

        # TRK Body data is equivalent to:
        # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
        self.body_column_names = None
        self.body_data = None

        self.__treated_body_column_names = None
        self.__treated_body_data = None

        # Fits information
        self.primary_hdu = None

    def convert_from_file(self, path, file_name, path_to_xml):
        """Loads data from a file and returns an `TRK` object.

        Parameters:
                path : pathlib.Path - Location of the TRK file in the file system.
                file_name : str - Name of the TRK file.
                path_to_xml : Path, optional - Location of the TRK xml description files in the file system.

        Raises:
                ValueError: If the filename is invalid.
        """

        # Extract values equivalent to TRK header
        # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
        self.header_column_names = self.__get_column_names(path_to_xml, POEMASDataType.HEADER)
        trk_header_column_names_list = list()
        for key, value in self.header_column_names.items():
            trk_header_column_names_list.append((key, value[1], value[0]))

        # Extract values equivalent to TRK body
        # sec, ele_ang, azi_ang, TB
        self.body_column_names = self.__get_column_names(path_to_xml, POEMASDataType.BODY)
        trk_data_column_names_list = list()
        for key, value in self.body_column_names.items():
            trk_data_column_names_list.append((key, value[1], value[0]))

        # Extract values from file that is going to be converted
        # Values will match values from respective lists

        # First, the header is extracted
        # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
        # That's why we set count=1, otherwise all data will from file will be classified as header

        # Then, data is extracted
        # sec, ele_ang, azi_ang, TB
        # This data is interspersed, since we want to keep reading it, we don't set count
        # We set count=1 at first to read only the header, then we set offset=28 because we already read the header
        if isinstance(path, bytes):
            self.header_data = np.frombuffer(path, trk_header_column_names_list, count=1)
            self.body_data = np.frombuffer(path, trk_data_column_names_list, offset=28)
        else:
            self.header_data = np.fromfile(str(path), trk_header_column_names_list, count=1)
            self.body_data = np.fromfile(str(path), trk_data_column_names_list, offset=28)

        # Get date according to julian day pattern
        self.date, self.time = self.__get_date().split(" ")

        # Get number of records present on file (NRS)
        self.records = self.header_data[0][1]

        # Treat TRK data
        # Keep in mind that the TB field comes in chunks of 400 items,
        # That way we need to create a new header to separate TB cases
        # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
        self.__treated_body_column_names = self.__get_column_names(path_to_xml, POEMASDataType.FULL_BODY)

        # Here we'll treat body data position, to fix interspersed
        self.__treat_trk_body_data()

        # Get time span of records
        self.start_time, self.end_time = self.__get_time_span()

        # Create fits Primary Header Data Unit (HDU)
        self.primary_hdu = create_primary_hdu(self.date,
                                              self.start_time,
                                              self.end_time,
                                              POEMAS_FULL_NAME,
                                              POEMAS_LATITUDE_LONGITUDE_HEIGHT,
                                              CASLEO,
                                              GMT_NEGATIVE_3,
                                              TRK_TYPE,
                                              file_name,
                                              POEMAS_TRK,
                                              POEMAS_FREQUENCY)

        self.body_column_names = self.__treated_body_column_names
        self.body_data = self.__treated_body_data

        return self

    def __get_column_names(self, path_to_xml, xml_type):
        """ Method for finding the correct description file.
        Returns a dict representing the description found,
        the key is the variable name and the value is a list
        containing the var dimension, type and unit respectively.
        """
        try:
            xml_path = PATH_TO_XML_TRK_COLUMN_NAME[xml_type]
        except KeyError:
            raise ValueError(INVALID_XML_FILE.format(xml_type))

        xml = xmlet.parse(path_to_xml / Path(xml_path)).getroot()

        header = collections.OrderedDict()

        for child in xml:
            var_name = child[0].text
            var_dim = int(child[1].text)
            var_type = child[2].text
            var_unit = child[3].text

            np_type = XML_TYPE_TO_NUMPY_TYPE[var_type]

            header.update({var_name: [var_dim, np_type, var_unit]})

        return header

    def __get_time_span(self):
        """Returns a tuple containing the ISO time of the
        first and last record found in the data.
        """

        nonzero = self.body_data["sec"].nonzero()

        return (julday.time(int(self.body_data["sec"][nonzero[0][0]])),
                julday.time(int(self.body_data["sec"][nonzero[0][-1]])))

    def __get_date(self):
        """Returns a string containing the ISO date and time of the
        first record found in the data.
        """
        nonzero = self.body_data["sec"].nonzero()

        date = str(julday.date(int(self.body_data["sec"][nonzero[0][0]])) + " " +
                   julday.time(int(self.body_data["sec"][nonzero[0][0]])))

        return date

    def __treat_trk_body_data(self):
        # We currently have our body data inside self.trk_body_data stored like this:
        # [  [sec, ele_ang, azi_ang, [TBL_45, TBR_45, TBL_90, TBR_90, TBL_45, TBR_45, ...],
        #    [sec, ele_ang, azi_ang, [TBL_45, TBR_45, TBL_90, TBR_90, TBL_45, TBR_45, ...],
        #                       .........................
        #    [sec, ele_ang, azi_ang, [TBL_45, TBR_45, TBL_90, TBR_90, TBL_45, TBR_45, ...]  ]
        # The number of arrays like this in self.trk_body_data is equivalent to self.records

        # To make things easier, we need to create 7 arrays to keep data from the same "family" together
        # [[sec, sec, ..., sec], [ele_ang, ele_ang, ..., ele_ang], ... [TBR_90, TBR_90, ..., TBR_90]]
        # That way we'll have 7 arrays, each one with size equivalent to self.records

        # TRK original data fields
        # sec, ele_ang, azi_ang, TB
        # We'll use names as iterators to better understand the procedure
        original_data_fields = ['sec', 'ele_ang', 'azi_ang', 'TB']

        # 7 arrays to represent each body data category
        # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
        self.__treated_body_data = [[], [], [], [], [], [], []]

        # This loop pass through self.trk_body_data arrays
        for record in range(0, self.records):
            field_position = 0

            # In this loop we look inside the self.trk_body_data arrays and check
            # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
            for field in original_data_fields:

                if field == 'sec':
                    sec = julday.sec(int(self.body_data[record][field_position]))
                    time = julday.time(sec)
                    final_sec_field = np.repeat(time, 100)
                    self.__treated_body_data[field_position].extend(final_sec_field)

                elif field == 'ele_ang' or field == 'azi_ang':
                    ang = np.repeat(self.body_data[record][field_position], 100)
                    self.__treated_body_data[field_position].extend(ang)

                elif field == 'TB':
                    # Here we apply transposition, to better understand this operation, check the following content:
                    # https://en.wikipedia.org/wiki/Transpose
                    # https://www.geeksforgeeks.org/transpose-matrix-single-line-python/
                    # Basically, we switch columns to rows
                    # We do this because the data inside TB is interspersed
                    # [TBL_45, TBR_45, TBL_90, TBR_90, TBL_45, TBR_45, TBL_90, TBR_90, TBL_45, ...]

                    # So first, we reshape the array size, to obtain this:
                    # [TBL_45, TBR_45, TBL_90, TBR_90,
                    #  TBL_45, TBR_45, TBL_90, TBR_90,
                    #       .....
                    #  TBL_45, TBR_45, TBL_90, TBR_90]

                    # Then we transpose it, to obtain this:
                    # [TBL_45, TBL_45, TBL_45, ..., TBL_45,
                    #  TBR_45, TBR_45, TBR_45, ..., TBR_45,
                    #           ......
                    #  TBR_90, TBR_90, TBR_90, ..., TBR_90]

                    tb_array = self.body_data[record][field_position].reshape(100, 4)
                    tb_array = tb_array.transpose()

                    # We know that TBs start at 3
                    # sec, ele_ang, azi_ang, >>TB<<
                    # But we have 4 different categories
                    # TBL_45, TBR_45, TBL_90, TBR_90
                    tb_category = 3

                    for tb in tb_array:
                        self.__treated_body_data[tb_category].extend(tb)
                        tb_category += 1

                field_position += 1
