# Instruments
SST_INSTRUMENT = 'SST'
POEMAS_INSTRUMENT = 'POEMAS'

# File types
TRK_TYPE = 'TRK'
RBD_TYPE = 'RBD'

# Instrument Types
AVAILABLE_SST_TYPES = {
    RBD_TYPE: ["bi", "rs", "rf"]
}
AVAILABLE_POEMAS_TYPES = {
    TRK_TYPE: ["TRK"]
}
INSTRUMENT_TO_TYPE_MAP = {
    SST_INSTRUMENT: AVAILABLE_SST_TYPES,
    POEMAS_INSTRUMENT: AVAILABLE_POEMAS_TYPES
}

# Errors
OBJECTS_NOT_FROM_SAME_INSTRUMENT = "Objects are not from the same instrument: {}"
CONCATENATE_NOT_AVAILABLE_ERROR = "Concatenate operation not available for file with type {} from instrument {}"
FILE_NOT_FOUND_ERROR = "File not found: {}"
INVALID_PATH_TO_XML_ERROR = "Invalid path to XML: {}"
INVALID_INSTRUMENT_ERROR = "Invalid instrument: {}"
INVALID_FILE_TYPE_ERROR = "Invalid file type {} for instrument {}."
INVALID_FILE_NAME = "Invalid filename {}"
INVALID_XML_FILE = "Invalid xml type: {}"
FILE_ALREADY_EXISTS = "File {} already exists."
INVALID_LEVEL_TYPE = "This level type is not valid: {}. It must be a integer"
FITS_LEVEL_NOT_AVAILABLE = "Fits level {} is not available for conversion"
CANT_CONVERT_FITS_LEVEL = "Can't get fits level {} for object with level {}, please try a level higher than {}"
COULDNT_MATCH_CONVERTED_DATA_TO_INSTRUMENT = "Couldn't match converted data fom file type {} to instrument {}"

# Others
XML_TABLE_PATH = "xml-tables/{}/{}"
CONCATENATED_DATA = "Concatenated Data"
