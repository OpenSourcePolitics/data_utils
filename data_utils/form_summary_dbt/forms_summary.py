from .card_creation import (
    Filter,
    Aggregation,
    Fields,
    Order,
    PieChart,
    TableChart,
    BarChart,
    HorizontalBarChart
)
from ..utils import MTB


class FormsSummary:
    def __init__(self, forms_parameters):
        self.forms_parameters = forms_parameters
        self.decidim_questionnaire_id = forms_parameters['DECIDIM_QUESTIONNAIRE_ID']
        self.database_id = forms_parameters['DATABASE_ID']

        res = MTB.create_collection(
            forms_parameters['FORM_NAME'],
            parent_collection_id=forms_parameters['COLLECTION_ID'],
            return_results=True
        )
        self.collection_id = res['id']

        self.get_questions_parameters()


    # TODO : move to table chart with dataset = True
    def create_form_model(self, answers_model_id, name, collection_id=0):
        params = {
            'name': name,
            'display': 'table',
            'dataset': True,
            'dataset_query': {
                'database': self.database_id,
                'query':
                    {
                        'filter':
                        [
                            '=',
                            [
                                'field',
                                'decidim_questionnaire_id',
                                {'base-type': 'type/Integer'}
                            ],
                            self.forms_parameters['DECIDIM_QUESTIONNAIRE_ID']
                        ],
                        'source-table': f'card__{answers_model_id}'
                    },
                'type': 'query'
            },
            'collection_id': collection_id
        }

        res = MTB.create_card(custom_json=params, return_card=True)
        self.form_model_info = res
        self.form_model_id = res['id']

    def get_questions_parameters(self):
        import pandas as pd

        sql_query = f"""
            SELECT DISTINCT question_title, question_type, position
            FROM prod.forms_answers
            WHERE decidim_questionnaire_id = {self.decidim_questionnaire_id}
            ORDER BY position;
        """

        # API request payload for Metabase
        query_payload = {
            "type": "native",
            "native": {
                "query": sql_query
            },
            "database": self.database_id
        }

        # Execute the query using Metabase API
        response = MTB.post("/api/dataset", json=query_payload)

        # Check if the response is valid
        if "data" in response and "rows" in response["data"]:
            df = pd.DataFrame(response["data"]["rows"], columns=["question_title", "question_type", "position"])
        else:
            raise ValueError("Failed to fetch data from Metabase API.")

        # Store questions in a structured format
        self.questions_parameters = df.values.tolist()


    def create_question_summary(self):
        chart_list = []

        for question in self.questions_parameters:
            question_title, question_type, position = question
            chart = None
            question_name = f"{position}. {question_title}"

            base_query = f"FROM prod.forms_answers WHERE decidim_questionnaire_id = {self.decidim_questionnaire_id} AND position = {position}"

            if question_type in ["short_answer", "long_answer"]:
                query = f"SELECT answer {base_query} AND answer NOT LIKE '%Pas de réponse%';"
                chart = TableChart(question_name, self, query=query)

            elif question_type in ["single_option"]:
                query = f"""
                    SELECT answer, COUNT(*) AS count 
                    {base_query} 
                    GROUP BY answer 
                    ORDER BY count DESC;
                """
                chart = PieChart(question_name, self, query=query)

            elif question_type in ["multiple_option"]:
                query = f"""
                    SELECT answer, COUNT(*) AS count 
                    {base_query} 
                    GROUP BY answer 
                    ORDER BY count DESC;
                """
                chart = BarChart(question_name, self, query=query)

            elif question_type in ["matrix_single", "matrix_multiple"]:
                query = f"""
                    SELECT sub_matrix_question, answer, COUNT(*) AS count 
                    {base_query} 
                    GROUP BY sub_matrix_question, answer 
                    ORDER BY count DESC;
                """
                chart = BarChart(question_name, self, query=query)

            elif question_type in ["files"]:
                query = f"SELECT answer, custom_body {base_query};"
                chart = TableChart(question_name, self, query=query)

            elif question_type in ["sorting"]:
                query = f"""
                    SELECT answer, SUM(sorting_points) AS total_points 
                    {base_query} 
                    GROUP BY answer 
                    ORDER BY total_points DESC;
                """
                chart = HorizontalBarChart(question_name, self, query=query)

            created_chart = chart.create_chart()
            chart_list.append([chart, created_chart])

        return chart_list
