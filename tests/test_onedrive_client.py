import unittest
from unittest.mock import patch, Mock

from onedrive_client import OneDriveClient

class TestOneDriveClient(unittest.TestCase):
    def setUp(self):
        self.client = OneDriveClient('token')

    @patch('onedrive_client.requests.put')
    def test_upload_file_calls_api(self, mock_put):
        mock_response = Mock(status_code=201)
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response
        with open('temp.txt', 'w') as f:
            f.write('data')
        self.client.upload_file('temp.txt', 'test.txt')
        mock_put.assert_called()

    @patch('onedrive_client.requests.get')
    def test_download_file_calls_api(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b'data'])
        mock_get.return_value = mock_response
        self.client.download_file('test.txt', 'out.txt')
        mock_get.assert_called()

if __name__ == '__main__':
    unittest.main()
