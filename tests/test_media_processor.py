import os
import unittest
from unittest.mock import patch, MagicMock

from media_processor import process_audio_file, process_video_file, process_text_file

class TestMediaProcessor(unittest.TestCase):
    def test_process_audio_file_notation_stub(self):
        with patch('media_processor.sr', None):
            result = process_audio_file('song.wav', 'notation')
            self.assertIn('notation', result)

    def test_process_audio_file_tab_stub(self):
        with patch('media_processor.sr', None):
            result = process_audio_file('song.mp3', 'tab')
            self.assertIn('tab', result)

    def test_process_video_file_stub(self):
        with patch('media_processor.shutil.which', return_value=None):
            result = process_video_file('movie.mp4')
            self.assertIn('predictive analysis', result)

    def test_process_audio_file_with_sr(self):
        fake_recognizer = MagicMock()
        fake_recognizer.record.return_value = 'audio'
        fake_recognizer.recognize_sphinx.return_value = 'hello world'
        fake_audiofile = MagicMock()
        fake_audiofile.__enter__.return_value = 'src'

        fake_sr = MagicMock()
        fake_sr.Recognizer.return_value = fake_recognizer
        fake_sr.AudioFile.return_value = fake_audiofile
        fake_sr.UnknownValueError = Exception
        fake_sr.RequestError = Exception

        with patch('media_processor.sr', fake_sr):
            result = process_audio_file('song.wav')
            self.assertIn('hello world', result)

    def test_process_video_file_ffprobe(self):
        with patch('media_processor.shutil.which', return_value='/usr/bin/ffprobe'):
            with patch('media_processor.subprocess.check_output', return_value='12.0'):
                result = process_video_file('movie.mp4')
                self.assertIn('12.00', result)

    def test_process_text_file(self):
        path = 'temp.txt'
        with open(path, 'w') as f:
            f.write('Hello world. This is a test.')
        result = process_text_file(path)
        self.assertIsInstance(result, str)
        os.remove(path)

if __name__ == '__main__':
    unittest.main()
