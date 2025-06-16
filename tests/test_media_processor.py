import os
import unittest
import numpy as np
import soundfile as sf

from media_processor import process_audio_file, process_video_file, process_text_file

class TestMediaProcessor(unittest.TestCase):
    def setUp(self):
        sr = 22050
        t = np.linspace(0, 0.5, int(sr * 0.5), False)
        tone = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write('song.wav', tone, sr)
        sf.write('song.mp3', tone, sr)

    def tearDown(self):
        os.remove('song.wav')
        os.remove('song.mp3')

    def test_process_audio_file_notation(self):
        result = process_audio_file('song.wav', 'notation')
        self.assertIn('Clef', result)

    def test_process_audio_file_tab(self):
        result = process_audio_file('song.mp3', 'tab')
        # Tab contains lines separated by newlines
        self.assertIn('-', result)

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
