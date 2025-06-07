import os
import unittest

from media_processor import process_audio_file, process_video_file, process_text_file

class TestMediaProcessor(unittest.TestCase):
    def test_process_audio_file_notation(self):
        result = process_audio_file('song.wav', 'notation')
        self.assertIn('notation', result)

    def test_process_audio_file_tab(self):
        result = process_audio_file('song.mp3', 'tab')
        self.assertIn('tab', result)

    def test_process_video_file(self):
        result = process_video_file('movie.mp4')
        self.assertIn('predictive analysis', result)

    def test_process_text_file(self):
        path = 'temp.txt'
        with open(path, 'w') as f:
            f.write('Hello world. This is a test.')
        result = process_text_file(path)
        self.assertIsInstance(result, str)
        os.remove(path)

if __name__ == '__main__':
    unittest.main()
