from craamvert.instruments import HISTORY, CONVERTED_WITH_FITS_LEVEL
from instruments.utils.fits_handlers import set_fits_file_name_and_output_path
from craamvert.instruments.poemas import POEMASDataType, POEMAS_FITS_FILE_NAME
from craamvert.instruments.poemas.utils.create_hdu import create_data_hdu
from craamvert.utils import CANT_CONVERT_FITS_LEVEL, POEMAS_INSTRUMENT, TRK_TYPE, \
    COULDNT_MATCH_CONVERTED_DATA_TO_INSTRUMENT
import numpy as np
from astropy.io import fits

from instruments.instrument import Instrument
from instruments.poemas.trk import trk

# Please check python docs to further understand this class
# https://docs.python.org/3/library/abc.html
# https://docs.python.org/3/tutorial/classes.html#inheritance
# https://docs.python.org/3/tutorial/classes.html#tut-private


class POEMAS(Instrument):

    def __init__(self):

        # Call for Instrument attributes
        super().__init__(instrument=POEMAS_INSTRUMENT)

        # POEMAS information
        self._records = None

        # POEMAS Header data is equivalent to:
        # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
        self._poemas_header_column_names = None
        self._poemas_header_data = None

        # POEMAS Body data is equivalent to:
        # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
        self._poemas_body_column_names = None
        self._poemas_body_data = None

        # Fits information
        self._primary_hdu_position = 0

    @staticmethod
    def open_file(file_name):
        poemas_object = POEMAS()

        poemas_object._verify_original_file_type(file_name)
        poemas_object._verify_original_file_path()
        poemas_object._set_path_to_xml()
        poemas_object._get_converted_data()

        return poemas_object

    def write_fits(self, name=None, output_path=None):
        # Create fits Binary Header Data Unit (HDU) to keep POEMAS header data
        # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
        poemas_header_hdu = create_data_hdu(self._poemas_header_column_names,
                                            self._poemas_header_data,
                                            POEMASDataType.HEADER)

        # Create fits Binary Header Data Unit (HDU) to keep POEMAS data
        # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
        poemas_data_hdu = create_data_hdu(self._poemas_body_column_names,
                                          self._poemas_body_data,
                                          POEMASDataType.BODY)

        # Create HDU list with all HDUs created until now
        hdu_list = fits.HDUList([self._primary_hdu, poemas_header_hdu, poemas_data_hdu])

        hdu_list[self._primary_hdu_position].header.append((HISTORY, CONVERTED_WITH_FITS_LEVEL
                                                            .format(self._fits_level)))

        fits_file_name, fits_output_path = set_fits_file_name_and_output_path(name,
                                                                              output_path,
                                                                              self._date,
                                                                              self._start_time,
                                                                              self._end_time,
                                                                              self._original_file_type,
                                                                              self._fits_level,
                                                                              POEMAS_FITS_FILE_NAME)
        hdu_list.writeto(fits_output_path / fits_file_name)

    def _get_converted_data(self):

        poemas_available_converters = {
            TRK_TYPE: trk.TRK().convert_from_file(self._original_file_path,
                                                  self._original_file_name,
                                                  self._path_to_xml)
        }
        converted_data = poemas_available_converters.get(self._original_file_type)

        self._match_type_object_attributes_to_instrument_attributes(converted_data)

    def _match_type_object_attributes_to_instrument_attributes(self, converted_data):
        try:
            # Match general information
            self._date = converted_data.date
            self._time = converted_data.time
            self._start_time = converted_data.start_time
            self._end_time = converted_data.end_time
            self._records = converted_data.records

            # Match data information
            # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
            self._poemas_header_column_names = converted_data.header_column_names
            self._poemas_header_data = converted_data.header_data

            # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
            self._poemas_body_column_names = converted_data.body_column_names
            self._poemas_body_data = converted_data.body_data

            # Match Fits information
            self._primary_hdu = converted_data.primary_hdu

        except AttributeError:
            print(COULDNT_MATCH_CONVERTED_DATA_TO_INSTRUMENT.format(self._instrument, self._original_file_type))

    # -------------------------------------------------------------
    # POEMAS specific methods
    # -------------------------------------------------------------

    def level_1(self):
        if self._fits_level != 0:
            raise ValueError(CANT_CONVERT_FITS_LEVEL.format(1, self._fits_level, self._fits_level))

        # Fits level 1 for POEMAS consists in reducing the data by calculating the median
        # from all data inside 1 second mark, meaning that the records will be reduced
        # we'll have only seconds registered, instead of milliseconds

        # POEMAS body data category size
        # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
        body_data_category_size = 7

        # 7 arrays to represent each body data category
        body_data = [[], [], [], [], [], [], []]

        # Here we prepare variables that will be used inside our loop
        # We'll keep track of chunks of data, these chunks represents all data inside a second mark
        original_data_position = 0
        is_inside_data_chunk = False

        # Our loop limit will be the size of data
        loop_limit = len(self._poemas_body_data[0])

        for data_position in range(0, loop_limit):
            # Here we check which second mark we're looking
            time_data = self._poemas_body_data[0][data_position]
            time_data = time_data[3:-3]

            # When not inside the data chunk it means that we're looking inside a new second mark
            if not is_inside_data_chunk:
                initial_second_mark = current_second_mark = time_data
                original_data_position = data_position
                is_inside_data_chunk = True
            else:
                current_second_mark = time_data

            # When we finish to look inside a second mark, we have to calculate the median
            # and store the result inside our new array
            if int(initial_second_mark) != int(current_second_mark) or data_position + 1 == loop_limit:
                # First we store which second mark we're looking
                body_data[0].append(self._poemas_body_data[0][original_data_position])

                # Here we calculate the median of all other data
                # ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
                for field in range(1, body_data_category_size):
                    slice_section = slice(original_data_position, data_position)
                    data_chunk = self._poemas_body_data[field][slice_section]
                    median = np.median(data_chunk)
                    body_data[field].append(median)

                # Then we update our chunk tracker
                is_inside_data_chunk = False

        # Here we update our object attributes with the new data
        self._poemas_body_data = body_data
        self._fits_level = 1

        # Here we update the header data
        # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
        # Update NRS
        self._poemas_header_data[0][1] = len(self._poemas_body_data[0][1])

        # Finally que update our fits level
        self._fits_level = 1

    def level_2(self, poemas_objects_list):
        if self._fits_level != 1:
            raise ValueError(CANT_CONVERT_FITS_LEVEL.format(2, self._fits_level, self._fits_level))

        # Fits level 2 for POEMAS consists in group all data from a day into a single fits file

        # Here we sort all poemas objects from a day, so they will be in ascending order
        poemas_objects_list.append(self)
        poemas_objects_list.sort(key=lambda poemas_object: poemas_object._start_time)

        # 7 arrays to represent each body data category
        # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
        body_data = [[], [], [], [], [], [], []]
        body_data_category_size = 7

        # Here we group all data form poemas objects to a new array
        for poemas_object in poemas_objects_list:
            for body_data_category in range(0, body_data_category_size):
                body_data[body_data_category].extend(poemas_object._poemas_body_data[body_data_category])

        # Here we update our object attributes with the new data
        self._poemas_body_data = body_data

        # Here we update the header data
        # Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
        total_nrs = 0
        brt_min_list = []
        brt_max_list = []

        # Gather all information
        for poemas_object in poemas_objects_list:
            total_nrs += poemas_object._poemas_header_data[0]["NRS"]
            brt_min_list.append(poemas_object._poemas_header_data[0]["BRTMin"])
            brt_max_list.append(poemas_object._poemas_header_data[0]["BRTMax"])

        # Update header information
        self._poemas_header_data[0]["NRS"] = total_nrs
        self._poemas_header_data[0]["BRTMin"] = min(brt_min_list)
        self._poemas_header_data[0]["BRTMax"] = max(brt_max_list)

        # We also update some basic information
        self._time = poemas_objects_list[0]._time
        self._start_time = poemas_objects_list[0]._start_time

        last_object_position = len(poemas_objects_list) - 1
        self._end_time = poemas_objects_list[last_object_position]._end_time

        # Finally we update our fits level
        self._fits_level = 2
