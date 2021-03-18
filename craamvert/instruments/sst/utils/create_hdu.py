from astropy.io import fits

from craamvert.instruments import NUMPY_TYPE_TO_T_FORM_TYPE


def create_data_hdu(column_names, data_array):
    """Create fits Binary Header Data Unit (HDU)

    Param:
         column_names
         data_array
         data_type

    Return:
         BinTableHDU
    """

    # Prepare fits column
    fits_columns = list()

    # Here, the column name is matched to the data array
    # To better understand this procedure please check astropy docs
    # https://docs.astropy.org/en/stable/io/fits/#working-with-table-data

    for column, values in column_names.items():
        numpy_type = values[1]
        t_format = NUMPY_TYPE_TO_T_FORM_TYPE[numpy_type]

        offset = 0
        if t_format != "I":
            offset = 32768

        fits_columns.append(fits.Column(
            name=column,
            format=t_format,
            unit=values[2],
            bscale=1.0,
            bzero=offset,
            array=data_array[column]
        ))

        sst_hdu = fits.BinTableHDU.from_columns(fits.ColDefs(fits_columns))

        return sst_hdu
