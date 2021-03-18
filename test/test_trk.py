import unittest
from unittest.mock import patch

from craamvert.instruments.poemas.trk.trk import TRK
from test.utils.trk_test_data import a_valid_trk_treated_body_column_names, a_valid_trk_header_data, \
    a_valid_trk_body_data, a_valid_trk_file_name, a_valid_trk_treated_body_data, a_valid_path_to_xml, a_valid_path


class TestTRK(unittest.TestCase):
    # Here we're testing with the data is correctly treated by TRK.__treat_trk_body_data()
    @patch('craamvert.instruments.poemas.trk.trk.np.fromfile')
    def test_convert_from_file(self, mock_numpy_fromfile):
        # First we create mocked data
        file_name = a_valid_trk_file_name()
        path = a_valid_path()
        path_to_xml = a_valid_path_to_xml()

        mock_numpy_fromfile.side_effect = [a_valid_trk_header_data(), a_valid_trk_body_data()]

        # Then we make the call
        returned_trk_object = TRK().convert_from_file(path, file_name, path_to_xml)

        # Now we check the results
        actual_body_data = returned_trk_object.body_data
        expected_body_data = a_valid_trk_treated_body_data()

        self.assertEqual(actual_body_data, expected_body_data)

        actual_body_column_data = returned_trk_object.body_column_names
        expected_body_column_names = a_valid_trk_treated_body_column_names()

        self.assertEqual(actual_body_column_data, expected_body_column_names)
