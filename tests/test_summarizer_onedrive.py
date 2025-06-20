import unittest
from unittest.mock import patch, Mock
from summarizer import main

class TestSummarizerOneDrive(unittest.TestCase):
    @patch('summarizer.OneDriveClient')
    def test_cli_upload(self, mock_client):
        # Prepare mocks
        instance = mock_client.return_value
        instance.upload_file.return_value = None
        with open('file.txt', 'w') as f:
            f.write('content')
        argv = ['summarizer.py', 'file.txt', '-o', 'out.txt', '--onedrive-path', 'Docs/out.txt', '--access-token', 'tok']
        with patch('sys.argv', argv):
            main()
        mock_client.assert_called_with('tok')
        instance.upload_file.assert_called()

if __name__ == '__main__':
    unittest.main()
