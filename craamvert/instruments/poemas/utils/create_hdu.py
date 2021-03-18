from astropy.io import fits

from craamvert.instruments import NUMPY_TYPE_TO_T_FORM_TYPE
from craamvert.instruments.poemas import POEMASDataType


def create_data_hdu(column_names, data_array, data_type):
    """Create fits Binary Header Data Unit (HDU)

    Param:
        column_names
        data_array
        data_type

    Return:
        BinTableHDU
    """
    if type(data_type) != POEMASDataType:
        raise ValueError("Wrong type for {}, should be POEMASDataType".format(data_type))

    # Prepare fits column
    fits_columns = list()

    # Here, the column name is matched to the data array
    # To better understand this procedure please check astropy docs
    # https://docs.astropy.org/en/stable/io/fits/#working-with-table-data

    # Here we create a data_position to be used as a counter, when creating column for TRK body data
    # TRK body data is composed of 11 arrays with data,
    # each array contains data from a different category:
    # sec, ele_ang, azi_ang, TBL_45, TBR_45, TBL_90, TBR_90 respectively
    # we use data_position to know which array to access according to the category (TRK body column names items)
    data_position = 0

    for column, values in column_names.items():
        numpy_type = values[1]
        t_format = NUMPY_TYPE_TO_T_FORM_TYPE[numpy_type]

        position = column if data_type == POEMASDataType.HEADER else data_position

        fits_columns.append(fits.Column(
            name=column,
            format=t_format,
            unit=values[2],
            array=data_array[position]
        ))

        data_position += 1

    poemas_hdu = fits.BinTableHDU.from_columns(fits.ColDefs(fits_columns))

    return poemas_hdu

