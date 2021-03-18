from collections import OrderedDict
import numpy as np
from pathlib import Path

# Array sizes
TB_ARRAY_SIZE = 400
CONVERTED_DATA_ARRAY_SIZE = 100

# Valid header data
VALID_CODE = 12345
VALID_NRS = 1
VALID_FREQ_NO = 2
VALID_FREQ_1 = 45.
VALID_FREQ_2 = 90.
VALID_BRT_MIN = 123.45
VALID_BRT_MAX = 123.45

# Valid body data
VALID_SEC = 349354295
VALID_DATE = '2012-01-27'
VALID_CONVERTED_TIME = '10:51:35'
VALID_ELE_ANG = 12
VALID_AZI_ANG = 12
VALID_TB = 900


TRK_HEADER_DATA_TYPE = [('Code', np.int32, 1),
                        ('NRS', np.int32, 1),
                        ('FreqNo', np.int32, 1),
                        ('Freq1', np.float32, 1),
                        ('Freq2', np.float32, 1),
                        ('BRTMin', np.float32, 1),
                        ('BRTMax', np.float32, 1)]

TRK_BODY_DATA_TYPE = [('sec', np.int32, 1),
                      ('ele_ang', np.float32, 1),
                      ('zi_ang', np.float32, 1),
                      ('TB', np.float32, TB_ARRAY_SIZE)]

TRK_TREATED_BODY_DATA_TYPE = [('sec', np.int32, 1),
                              ('ele_ang', np.float32, 1),
                              ('zi_ang', np.float32, 1),
                              ('TBL_45', np.float32, CONVERTED_DATA_ARRAY_SIZE),
                              ('TBR_45', np.float32, CONVERTED_DATA_ARRAY_SIZE),
                              ('TBL_90', np.float32, CONVERTED_DATA_ARRAY_SIZE),
                              ('TBR_90', np.float32, CONVERTED_DATA_ARRAY_SIZE)]


def a_valid_path_to_xml():
    main_path = str(Path(__file__).parent)[:-11]
    return Path(main_path) / Path("craamvert/instruments/xml-tables/POEMAS/TRK")


def a_valid_path():
    return Path("utils/").expanduser()


def a_valid_trk_file_name():
    return "SunTrack_120127_105135.TRK"


# sec, ele_ang, azi_ang, TB
def a_valid_trk_treated_body_column_names():
    return OrderedDict([('sec', [1, str, 'none']),
                        ('ele_ang', [1, np.float32, 'none']),
                        ('zi_ang', [1, np.float32, 'none']),
                        ('TBL_45', [1, np.float32, 'none']),
                        ('TBR_45', [1, np.float32, 'none']),
                        ('TBL_90', [1, np.float32, 'none']),
                        ('TBR_90', [1, np.float32, 'none'])])


# Code, NRS, FreqNo, Freq1, Freq2, BRTMin, BRTMax
def a_valid_trk_header_data():
    return np.array([(VALID_CODE, VALID_NRS, VALID_FREQ_NO, VALID_FREQ_1, VALID_FREQ_2, VALID_BRT_MIN, VALID_BRT_MAX)],
                    TRK_HEADER_DATA_TYPE)


# sec, ele_ang, azi_ang, TB
# there's 4 types of tb, they come in groups of 100
def a_valid_trk_body_data():
    tb = [VALID_TB] * TB_ARRAY_SIZE
    return np.array([(VALID_SEC, VALID_ELE_ANG, VALID_AZI_ANG, tb)], dtype=TRK_BODY_DATA_TYPE)


# sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90
def a_valid_trk_treated_body_data():
    sec = [VALID_CONVERTED_TIME] * CONVERTED_DATA_ARRAY_SIZE
    ele_ang = [VALID_ELE_ANG] * CONVERTED_DATA_ARRAY_SIZE
    azi_ang = [VALID_AZI_ANG] * CONVERTED_DATA_ARRAY_SIZE
    tbl_45 = tbr_45 = tbl_90 = tbr_90 = [VALID_TB] * CONVERTED_DATA_ARRAY_SIZE
    return [sec, ele_ang, azi_ang, tbl_45, tbr_45, tbl_90, tbr_90]
