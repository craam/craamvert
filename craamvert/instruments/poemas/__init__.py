from enum import Enum

POEMAS_FITS_FILE_NAME = "poemas-{}-D{}-T{}-{}-level{}.fits"

# POEMAS Header Data
POEMAS_FULL_NAME = 'POEMAS - POlarization Emission of Millimeter Activity at the Sun'
POEMAS_LATITUDE_LONGITUDE_HEIGHT = 'Lat = -31.79897222, Lon = -69.29669444, Height = 2.491 km'
POEMAS_TRK = 'POEMAS TRK Raw Binary Data file'
POEMAS_FREQUENCY = '45 GHz ch=R,L; 90 GHz ch=R,L'


class POEMASDataType(Enum):
    HEADER = "header"
    BODY = "body"
    FULL_BODY = "full_body"
