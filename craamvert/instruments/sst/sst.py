from craamvert.instruments import HISTORY, CONVERTED_WITH_FITS_LEVEL
from craamvert.instruments.sst import SST_FITS_FILE_NAME
from instruments.utils.fits_handlers import set_fits_file_name_and_output_path
from instruments.utils.hdu_handlers import add_sst_comments
from craamvert.instruments.sst.utils.create_hdu import create_data_hdu
from craamvert.utils import RBD_TYPE, COULDNT_MATCH_CONVERTED_DATA_TO_INSTRUMENT

from astropy.io import fits

from instruments.instrument import Instrument
from instruments.sst.rbd import rbd
from utils import SST_INSTRUMENT


# Please check python docs to further understand this class
# https://docs.python.org/3/library/abc.html
# https://docs.python.org/3/tutorial/classes.html#inheritance
# https://docs.python.org/3/tutorial/classes.html#tut-private


class SST(Instrument):

    def __init__(self):
        # Call for Instrument attributes
        super().__init__(instrument=SST_INSTRUMENT)

        # SST Data
        self.__sst_column_names = None
        self.__sst_data = None

        # Fits information
        self._primary_hdu_position = 0

    @staticmethod
    def open_file(file_name):
        sst_object = SST()

        sst_object._verify_original_file_type(file_name)
        sst_object._verify_original_file_path()
        sst_object._set_path_to_xml()
        sst_object._get_converted_data()

        return sst_object

    def write_fits(self, name=None, output_path=None):
        # Create fits Binary Header Data Unit (HDU) to keep SST data
        sst_hdu = create_data_hdu(self._sst_column_names, self._sst_data)

        add_sst_comments(sst_hdu)

        hdu_list = fits.HDUList([self._primary_hdu, sst_hdu])

        hdu_list[self._primary_hdu_position].header.append((HISTORY, CONVERTED_WITH_FITS_LEVEL
                                                            .format(self._fits_level)))

        fits_file_name, fits_output_path = set_fits_file_name_and_output_path(name,
                                                                              output_path,
                                                                              self._date,
                                                                              self._start_time,
                                                                              self._end_time,
                                                                              self._original_file_type,
                                                                              self._fits_level,
                                                                              SST_FITS_FILE_NAME)
        hdu_list.writeto(fits_output_path / fits_file_name)

    def _get_converted_data(self):

        sst_available_converters = {
            RBD_TYPE: rbd.RBD().convert_from_file(self._original_file_path, self._original_file_name,
                                                  self._path_to_xml)
        }
        converted_data = sst_available_converters.get(self._original_file_type)

        self._match_type_object_attributes_to_instrument_attributes(converted_data)

    def _match_type_object_attributes_to_instrument_attributes(self, converted_data):
        try:
            # Match general information
            self._date = converted_data.date
            self._time = converted_data.time
            self._start_time = converted_data.start_time
            self._end_time = converted_data.end_time

            # Match data information
            self._sst_column_names = converted_data.column_names
            self._sst_data = converted_data.data

            # Match Fits information
            self._primary_hdu = converted_data.primary_hdu

        except AttributeError:
            print(COULDNT_MATCH_CONVERTED_DATA_TO_INSTRUMENT.format(self._instrument, self._original_file_type))
