import numpy as np

# Fits Header Data
ORIGIN = 'origin'
ORIGIN_CRAAM = 'CRAAM/Universidade Presbiteriana Mackenzie'
TELESCOPE = 'telescop'
STATION = 'station'
OBSERVATION_DATE = 'date-obs'
START_TIME = 't_start'
END_TIME = 't_end'
DATA_TYPE = 'data_typ'
FILE_ORIGIN = 'origfile'
FREQUENCY = 'frequen'
HISTORY = 'history'
COMMENT = 'comment'

# Timezones
TIMEZONE = 'tz'
GMT_NEGATIVE_3 = 'GMT-3'

# Observatories
OBSERVATORY = 'observat'
CASLEO = 'CASLEO'

# Others
FITS_FILE_EXTENSION = ".fits"

XML_TYPE_TO_NUMPY_TYPE = {
    "xs:int": np.int32,
    "xs:float": np.float32,
    "xs:string": str,
    "xs:unsignedShort": np.uint16,
    "xs:short": np.uint16,
    "xs:byte": np.byte,
}

NUMPY_TYPE_TO_T_FORM_TYPE = {
    np.int32: "1J",
    np.float32: "1E",
    str: "20A",
    np.uint16: "I",
    np.int16: "I",
    np.byte: "B",
}

CONVERTED_WITH_FITS_LEVEL = "Converted to FITS level-{}"
