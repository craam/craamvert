import xml.etree.ElementTree as xmlet
from pathlib import Path

import numpy as np
import craamvert.utils.iso_time as time
from astropy.io import fits

from craamvert.instruments.sst import SST_FITS_FILE_NAME
from craamvert.utils import SST_INSTRUMENT, OBJECTS_NOT_FROM_SAME_INSTRUMENT, CONCATENATED_DATA, INVALID_FILE_NAME, FILE_ALREADY_EXISTS
from craamvert.instruments import ORIGIN_CRAAM, ORIGIN, TELESCOPE, SST_FULL_NAME, OBSERVATORY, CASLEO, STATION, \
    SST_LATITUDE_LONGITUDE_HEIGHT, TIMEZONE, GMT_NEGATIVE_3, OBSERVATION_DATE, START_TIME, END_TIME, FILE_ORIGIN, \
    SST_RBD, DATA_TYPE, FREQUENCY, SST_FREQUENCY, add_copyright, HISTORY, add_sst_comments, FITS_FILE_EXTENSION


def concatenate(rbds):
    """Method for concatenating RBDs. It returns a new RBD object
        representing the concatenated data ordered by time.

        Parameters:
            rbds : list, tuple - List or tuple of RBD objects to be concatenated. The objects must be from same type
        
        Raises
        ------
        TypeError
            If the objects have different data structures.
        """

    try:
        new_data = np.concatenate([rbd.body_data for rbd in rbds])
    except TypeError:
        raise TypeError(OBJECTS_NOT_FROM_SAME_INSTRUMENT.format(SST_INSTRUMENT))

    # Order the data by time
    new_data = new_data[new_data["time"].argsort()]

    rbd = RBD()

    filenames = list()
    for r in rbds:
        if isinstance(r.__filename, list):
            filenames.extend(r.__filename)
        else:
            filenames.append(r.__filename)

    filenames = sorted(filenames)

    rbd.__filename = filenames

    rbd.__type = rbds[0].__type
    rbd.__date = rbds[0].date
    rbd.__data = new_data

    date = filenames[0].split(".")
    time = "00:00"
    if len(date) > 1:
        time = date[1][:2] + ":" + date[1][2:4]

    rbd.__time = time

    rbd._header = rbds[0]._header
    rbd.__history.append(CONCATENATED_DATA)

    return rbd


class RBD:

    def __init__(self):
        self.__filename = ""
        self.__type = ""
        self.__date = ""
        self.__time = ""
        self.__data = np.empty((0))
        self.__history = list()
        self.__original_file_type = "RBD"

    def __add__(self, other):
        """
        Magic method for concatenating RBDs.
        Usage: rbd3 = rbd1 + rbd2
        """

        return concatenate((self, other))

    @property
    def __columns(self):
        """Returns the names of the columns in a tuple."""

        return self.__data.dtype.names

    def __reduced(self, columns=None):
        """Returns a reduced version of the RBD

        By default the reduced version contains:
             
             time    : time in Hus
             azipos  : encoder's azimuth
             elepos  : encoder's elevation
             adc or adcval : receiver's output
             opmode  : oberving mode
             target  : target observed
             x_off   : scan offset in azimuth
             y_off   : scan offset in elevation

        Parameters
        ----------
        columns : list, optional
            List of which columns the reduced version should contain.
        """

        if not columns:
            adc = "adc" if "adc" in self.__columns else "adcval"
            columns = ['time', adc, 'elepos', 'azipos',
                       'opmode', 'target', 'x_off', 'y_off']

        rbd = RBD()
        rbd.__filename = self.__filename
        rbd.__type = self.__type
        rbd.__date = self.__date
        rbd.__time = self.__time
        rbd._header = {column: self._header[column] for column in columns}
        rbd.__data = self.__data[[name for name in columns]]

        rbd.__history.append("Reduced Data File. Selected Variables saved")

        return rbd

    def get_time_span(self):
        """
        Returns a tuple containing the ISO time of the
        first and last record found in the data.
        """

        nonzero = self.__data["time"].nonzero()
        return (time.time(self.__data["time"][nonzero[0][0]]), time.time(self.__data["time"][nonzero[0][-1]]))

    def to_fits(self, name=None, output_path=None):
        """Writes the RBD data to a FITS file.

        By default the name of the fits file is defined as:

        sst_[integration | subintegration | auxiliary]_YYYY-MM-DDTHH:MM:SS.SSS-HH:MM:SS.SSS_level0.fits

        The file has two HDUs. The primary containing just a header with general
        information such as the origin, telescope, time zone. The second is a BinaryTable
        containing the data and a header with data specific information.

        Parameters
        ----------
        name : str, optional
            Name of the fits file.
        
        output_path : str, pathlib.Path, optional
            Output path of the fits file. By default
            is where the script is being called from.
        
        Raises
        ------
        FileExistsError
            If a file with the same name already exists
            in the output path.
        """

        t_start, t_end = self.get_time_span()

        if not name:
            name = SST_FITS_FILE_NAME.format(self.__type.lower(), self.__date, t_start, t_end)
        else:
            if not name.endswith(FITS_FILE_EXTENSION):
                name += FITS_FILE_EXTENSION

        name = Path(name)

        if not output_path:
            output_path = "."

        output_path = Path(output_path).expanduser()

        if (output_path / name).exists():
            raise FileExistsError(FILE_ALREADY_EXISTS.format(str(name)))

        hdu = fits.PrimaryHDU()
        hdu.header.append((ORIGIN, ORIGIN_CRAAM, ''))
        hdu.header.append((TELESCOPE, SST_FULL_NAME, ''))
        hdu.header.append((OBSERVATORY, CASLEO, ''))
        hdu.header.append((STATION, SST_LATITUDE_LONGITUDE_HEIGHT, ''))
        hdu.header.append((TIMEZONE, GMT_NEGATIVE_3, ''))

        hdu.header.append((OBSERVATION_DATE, self.__date, ''))
        hdu.header.append((START_TIME, self.__date + 'T' + t_start, ''))
        hdu.header.append((END_TIME, self.__date + 'T' + t_end, ''))
        hdu.header.append((DATA_TYPE, self.__type, ''))
        if isinstance(self.__filename, list):
            for fname in self.__filename: hdu.header.append((FILE_ORIGIN, fname, SST_RBD))
        else:
            hdu.header.append((FILE_ORIGIN, self.__filename, SST_RBD))

        hdu.header.append((FREQUENCY, SST_FREQUENCY, ''))

        # About the Copyright
        add_copyright(hdu)

        # History
        hdu.header.append((HISTORY, "Converted to FITS level-0 with rbd.py"))

        for hist in self.__history:
            hdu.header.append((HISTORY, hist))

        dscal = 1.0
        fits_cols = list()
        for column, values in self._header.items():

            var_dim = str(values[0])

            offset = 0
            if values[1] == np.int32:
                var_dim += "J"
            elif values[1] == np.uint16:
                var_dim += "I"
                offset = 32768
            elif values[1] == np.int16:
                var_dim += "I"
            elif values[1] == np.byte:
                var_dim += "B"
            elif values[1] == np.float32:
                var_dim += "E"

            fits_cols.append(fits.Column(name=column,
                                         format=var_dim,
                                         unit=values[2],
                                         bscale=dscal,
                                         bzero=offset,
                                         array=self.__data[column]))

        tbhdu = fits.BinTableHDU.from_columns(fits.ColDefs(fits_cols))

        add_sst_comments(tbhdu)

        hdulist = fits.HDUList([hdu, tbhdu])

        hdulist.writeto(output_path / name)

    def __find_header(self, path_to_xml):
        """
        Method for finding the correct description file.
        Returns a dict representing the description found,
        the key is the variable name and the value is a list
        containing the var dimension, type and unit respectively.
        """

        span_table = xmlet.parse(path_to_xml / Path("SSTDataFormatTimeSpanTable.xml")).getroot()
        filetype = "Data" if self.__type == "Integration" or self.__type == "Subintegration" else "Auxiliary"

        for child in span_table:
            if child[0].text == filetype and child[1].text <= self.__date and child[2].text >= self.__date:
                data_description_filename = child[3].text

        xml = xmlet.parse(path_to_xml / Path(data_description_filename)).getroot()

        header = dict()
        for child in xml:
            var_name = child[0].text
            var_dim = int(child[1].text)
            var_type = child[2].text
            var_unit = child[3].text

            if var_type == "xs:int":
                np_type = np.int32
            elif var_type == "xs:unsignedShort":
                np_type = np.uint16
            elif var_type == "xs:short":
                np_type = np.int16
            elif var_type == "xs:byte":
                np_type = np.byte
            elif var_type == "xs:float":
                np_type = np.float32

            header.update({var_name: [var_dim, np_type, var_unit]})

        return header

    def from_file(self, path, name, path_to_xml):
        """Loads data from a file and returns an `RBD` object.

        Parameters
        ----------
            path : pathlib.Path
                Location of the RBD file in the file system.

            name : str
                Name of the RBD file.

            path_to_xml : Path, optional
                Location of the RBD xml description files in the file system.

        Raises
        ------
        ValueError
            If the filename is invalid.
        """

        self.__filename = name
        type_prefix = self.__filename[:2].upper()

        if type_prefix == "RS":
            self.__type = "Integration"
        elif type_prefix == "RF":
            self.__type = "Subintegration"
        elif type_prefix == "BI":
            self.__type = "Auxiliary"
        else:
            raise ValueError(INVALID_FILE_NAME.format(self.__filename))

        date = self.__filename[2:].split(".")

        """
        date[0] = date[0][::-1]
        day = date[0][:2][::-1]
        month = date[0][2:4][::-1]
        year = int(date[0][4:][::-1]) + 1900
        self.date = "{}-{}-{}".format(year,month,day)
        """

        if len(date[0]) == 6:
            self.__date = str(int(date[0][:2]) + 1900) + '-' + date[0][2:4] + '-' + date[0][4:6]
        elif len(date[0]) == 7:
            self.__date = str(int(date[0][:3]) + 1900) + '-' + date[0][3:5] + '-' + date[0][5:7]
        else:
            raise ValueError(INVALID_FILE_NAME.format(self.__filename))

        self.__time = "00:00"
        if len(date) > 1:
            self.__time = date[1][:2] + ":" + date[1][2:4]

        self._header = self.__find_header(path_to_xml)

        dt_list = list()
        for key, value in self._header.items():
            dt_list.append((key, value[1], value[0]))

        if isinstance(path, bytes):
            self.__data = np.frombuffer(path, dtype=dt_list)
        else:
            self.__data = np.fromfile(str(path), dtype=dt_list)

        return self
