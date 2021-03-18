from craamvert.instruments import FITS_FILE_EXTENSION
from pathlib import Path

from craamvert.utils import FILE_ALREADY_EXISTS


def set_fits_file_name_and_output_path(name, output_path, date, start_time, end_time, original_file_type, fits_level,
                                       instrument_fits_file_name):
    """Define final fits file name and output path
    """

    new_separator = "_"
    new_date = date.split(":")
    new_date = new_separator.join(new_date)

    new_start_time = start_time.split(":")
    new_start_time = new_separator.join(new_start_time)

    new_end_time = end_time.split(":")
    new_end_time = new_separator.join(new_end_time)

    if not name:
        name = instrument_fits_file_name.format(original_file_type.lower(), new_date,
                                                new_start_time, new_end_time, fits_level)
    else:
        if not name.endswith(FITS_FILE_EXTENSION):
            name += FITS_FILE_EXTENSION

    fits_file_name = Path(name)

    if not output_path:
        output_path = ""

    fits_output_path = Path(output_path).expanduser()

    if (fits_output_path / fits_file_name).exists():
        raise FileExistsError(FILE_ALREADY_EXISTS.format(str(fits_file_name)))

    return fits_file_name, fits_output_path
