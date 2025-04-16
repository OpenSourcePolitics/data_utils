from form_filtering import answers_to_filters, dump_df_to_postgresql
import unittest
import pandas as pd

class TestDataframeProcessing(unittest.TestCase):

    def set_up_mock_data(self):
        self.mapping_raw = pd.DataFrame({
            'session_token': ['1038918792771835475219703', '1038918792771835475219703', '77819727802057982331067', '77819727802057982331067'],
            'question_type': ['single_option', 'single_option', 'single_option', 'single_option'],
            'question_title': ['Qu\'avez-vous contre les Caractères spéciaux ?', 'Pourquoi ?', 'Qu\'avez-vous contre les Caractères spéciaux ?', 'Pourquoi ?'],
            'anwser': ['Oui', 'Non', 'Rien du tout', 'NaN'],
            'decidim_questionnaire_id': ['1', '1', '1', '1'],
            'position': ['1', '2', '1', '3']
        })

    def test_df_pivoting(self):
        """Test that the form_answers dataframe is correctly pivoted and aggregated."""
        form_filters = answers_to_filters(self.mapping_raw)

        expected_columns = ['1._qu_avez-vous_contre_les_caractères_spéciaux_?', '2. pourquoi_?', '3. pourquoi_?']
        self.assertEqual(list(form_filters.columns), expected_columns)

if __name__ == '__main__':
    unittest.main()