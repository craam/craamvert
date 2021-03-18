from craamvert.instruments import COMMENT, ORIGIN, ORIGIN_CRAAM, TELESCOPE, OBSERVATORY, STATION, TIMEZONE, OBSERVATION_DATE, \
    START_TIME, END_TIME, DATA_TYPE, FILE_ORIGIN, FREQUENCY
from astropy.io import fits


def add_sst_comments(hdu):
    """Add SST comments"""
    hdu.header.append((COMMENT, 'Time is in hundred of microseconds (Hus) since 0 UT', ''))
    hdu.header.append((COMMENT, 'ADCu = Analog to Digital Conversion units. Proportional to Voltage', ''))
    hdu.header.append((COMMENT, 'mDeg = milli degree', ''))
    hdu.header.append((COMMENT, 'Temperatures are in Celsius', ''))


def create_primary_hdu(date, start_time, end_time, data_type,
                       instrument_full_name, instrument_latitude_longitude_height, observatory_name,
                       timezone_info, file_name, file_type, instrument_frequency):
    """Create fits Primary Header Data Unit (HDU) and add file info to it

    Parameter:
        date
        start_time
        end_time
        data_type
        file_name

    Return:
        PrimaryHDU
    """
    primary_hdu = fits.PrimaryHDU()
    primary_hdu.header.append((ORIGIN, ORIGIN_CRAAM, ''))
    primary_hdu.header.append((TELESCOPE, instrument_full_name, ''))
    primary_hdu.header.append((OBSERVATORY, observatory_name, ''))
    primary_hdu.header.append((STATION, instrument_latitude_longitude_height, ''))
    primary_hdu.header.append((TIMEZONE, timezone_info, ''))

    primary_hdu.header.append((OBSERVATION_DATE, date, ''))
    primary_hdu.header.append((START_TIME, date + 'T' + start_time, ''))
    primary_hdu.header.append((END_TIME, date + 'T' + end_time, ''))
    primary_hdu.header.append((DATA_TYPE, data_type, ''))

    if isinstance(file_name, list):
        for file_name in file_name:
            primary_hdu.header.append((FILE_ORIGIN, file_name, file_type))
    else:
        primary_hdu.header.append((FILE_ORIGIN, file_name, file_type))

    primary_hdu.header.append((FREQUENCY, instrument_frequency, ''))

    # About the Copyright
    primary_hdu.header.append(('comment', 'COPYRIGHT. Grant of use.', ''))
    primary_hdu.header.append(('comment', 'These data are property of Universidade Presbiteriana Mackenzie.'))
    primary_hdu.header.append(('comment', 'The Centro de Radio Astronomia e Astrofisica Mackenzie is reponsible'))
    primary_hdu.header.append(('comment', 'for their distribution. Grant of use permission is given for Academic '))
    primary_hdu.header.append(('comment', 'purposes only.'))

    return primary_hdu
