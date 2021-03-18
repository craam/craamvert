from abc import ABC, abstractmethod
from pathlib import Path
from re import search

from craamvert.utils import FILE_NOT_FOUND_ERROR, XML_TABLE_PATH, INVALID_FILE_TYPE_ERROR, INSTRUMENT_TO_TYPE_MAP


# Please check python docs to further understand this class
# https://docs.python.org/3/library/abc.html
# https://docs.python.org/3/library/functions.html#staticmethod
# https://docs.python.org/3/tutorial/classes.html#tut-private

class Instrument(ABC):
    def __init__(self, instrument):
        # All attributes must be declared on __init__

        # Original file data
        self._original_file_path = None
        self._original_file_name = None
        self._path_to_xml = None
        self._original_file_type = None

        # Instrument information
        self._instrument = instrument
        self._date = None
        self._time = None
        self._start_time = None
        self._end_time = None

        # Fits information
        self._fits_level = 0
        self._primary_hdu = None

    # -------------------------------------------------------------
    # Abstract methods
    # -------------------------------------------------------------

    @staticmethod
    @abstractmethod
    def open_file(file_name):
        """Open instrument file and return a instrument object

        Parameters:
               file_name : str, pathlib.Path, buffer - File to be opened.
        """
        pass

    @abstractmethod
    def write_fits(self, name=None, output_path=None):
        """
        Function to create a fits file with instrument information

        Parameters:
            name: str, optional
            output_path: str, optional
        """
        pass

    @abstractmethod
    def _get_converted_data(self):
        """Function to call converter according to original file type and return instrument object"""
        pass

    @abstractmethod
    def _match_type_object_attributes_to_instrument_attributes(self, converted_data):
        """Function to match attributes from converter to instruments attributes"""
        pass

    # -------------------------------------------------------------
    # Shared methods
    # -------------------------------------------------------------

    def _verify_original_file_type(self, file_name):
        """Function to verify if the file to be converted type is supported

        Parameters:
               file_name : str, pathlib.Path, buffer - File to be opened.

        Raises:
            ValueError: If instrument type is invalid or if file to be converted type is not supported
        """
        self._original_file_path = file_name

        available_instrument_types = INSTRUMENT_TO_TYPE_MAP[self._instrument]

        instrument_file_type = None

        # Check if file contains any of the necessary identifiers
        for available_type in available_instrument_types:
            for identifier in available_instrument_types[available_type]:
                if (search(identifier, self._original_file_path)) or (search(identifier, self._original_file_path)):
                    instrument_file_type = available_type

        if not instrument_file_type:
            raise ValueError(INVALID_FILE_TYPE_ERROR.format(self._original_file_path, self._instrument))
        else:
            self._original_file_type = instrument_file_type

    def _verify_original_file_path(self):
        """Function to verify if path of file to be converted exists

            Raises:
                FileNotFoundError: If the XML file for the instrument was not found.
        """
        if not isinstance(self._original_file_path, bytes):
            self._original_file_path = Path(self._original_file_path).expanduser()
        if not self._original_file_path.exists():
            raise FileNotFoundError(FILE_NOT_FOUND_ERROR.format(self._original_file_path))

        self._original_file_name = self._original_file_path.name

    def _set_path_to_xml(self):
        """Function to get xml compatible to the file to be converted

            Raises:
                ValueError: If the path to the xml files is invalid.
        """

        self._path_to_xml = Path(__file__).parent / Path(XML_TABLE_PATH.format(self._instrument,
                                                                               self._original_file_type))

        if not self._path_to_xml.exists():
            raise ValueError(INVALID_FILE_TYPE_ERROR.format(self._original_file_type, self._instrument))

    def get_fits_level(self):
        """Returns fits level

            Returns:
                str
        """
        return str(self._fits_level)

    def get_date(self):
        """Return observation date

            Returns:
                str
        """
        return str(self._date)

    def get_time(self):
        """Return observation time

            Returns:
                str
        """
        return str(self._time)

    def get_start_time(self):
        """Return observation start time

            Returns:
                str
        """
        return str(self._start_time)

    def get_end_time(self):
        """Return observation end time

            Returns:
                str
        """
        return str(self._end_time)


