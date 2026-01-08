from .forms_summary import clean_and_prepare_dataframe
from ..utils import MTB
import unittest
import pandas as pd
import numpy as np

class TestDataframeProcessing(unittest.TestCase):

    def setUp(self):
        self.language = 'en'
        self.df_single_option = pd.DataFrame({
            'session_token': ['420000', '530000', '420000', '530000'],
            'question_type': ['single_option', 'single_option', 'single_option', 'single_option'],
            'question_title': ['Souhaitez-vous venir ?', 'Souhaitez-vous venir ?', 'Avez-vous bu ?', 'Avez-vous bu ?'],
            'answer': ['Je souhaite venir car :', 'Je ne souhaite pas venir car :', 'Oui', 'Non'],
            'position': ['1', '1', '2', '2'],
            'custom_body': [np.nan, 'Je ne suis pas disponible', np.nan, np.nan]
        })

        self.df_multiple_option = pd.DataFrame({
            'session_token': ['420000', '420000', '530000', '530000'],
            'question_type': ['multiple_option', 'multiple_option', 'multiple_option', 'multiple_option'],
            'question_title': ['Couleurs préférées ?', 'Couleurs préférées ?', 'Couleurs préférées ?', 'Couleurs préférées ?'],
            'answer': ['Vert', 'Bleu', 'Vert', 'Bleu'],
            'position': ['3', '3', '3', '3'],
            'custom_body': [np.nan, 'ça me rappelle la mer', np.nan, np.nan]
        })
    
    def test_has_custom_body(self):
        """Test that the questions to which someone has answered with a custom body are detected."""
        data = clean_and_prepare_dataframe(self.df_single_option, self.language)
        expected_data = [
            ['Souhaitez-vous venir ?', 'single_option', '1', True],
            ['Avez-vous bu ?', 'single_option', '2', False]
        ]  
        self.assertEqual(data, expected_data)

    def test_has_custom_body_multiple_option(self):
        """Test that the questions to which someone has answered with a custom body are detected."""
        data = clean_and_prepare_dataframe(self.df_multiple_option, self.language)
        expected_data = [
            ['Couleurs préférées ?', 'multiple_option', '3', True]
        ]  
        self.assertEqual(data, expected_data)

if __name__ == '__main__':
    unittest.main()