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

def clean_and_prepare_dataframe(df, lang):
    df.columns = (
        df.columns.str.lower()
        .str.replace(' ', '_')
    )
    if lang == 'fr':
        df['has_custom_body'] = df['corps_personnalisé'].notna()
        df = df[
            ['titre_de_la_question', 'type_de_question', 'position', 'has_custom_body']
        ].drop_duplicates()
    elif lang == 'en':
        df['has_custom_body'] = df['custom_body'].notna()
        df = df[
            ['question_title', 'question_type', 'position', 'has_custom_body']
        ].drop_duplicates()
    else:
        raise NotImplementedError(
            "Provided language is not implemented yet"
        )
    df = df.\
        sort_values(by=['position', 'has_custom_body'], ascending=False).\
        drop_duplicates(subset='position', keep='first').\
        sort_values(by='position')
    return df.values.tolist()

class FormsSummary:
    def __init__(self, credentials):
        self.credentials = credentials
        self.form_id = credentials['FORM_ID']

        self.language = credentials['LANGUAGE']
        self.get_database_id()

        # Create collection for everything
        res = MTB.create_collection(
            credentials['FORM_NAME'],
            parent_collection_id=credentials['COLLECTION_ID'],
            return_results=True
        )
        self.collection_id = res['id']

        self.create_form_model(
            credentials['ANSWERS_MODEL_ID'],
            name=credentials['FORM_NAME'],
            collection_id=self.collection_id
        )

    def get_database_id(self):
        self.database_id = MTB.get_item_info(
            'card',
            self.credentials['ANSWERS_MODEL_ID']
        )["database_id"]

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
                            self.credentials['FORM_ID']
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
        res = MTB.get_card_data(card_id=self.form_model_id)
        df = pd.DataFrame(res)

        return clean_and_prepare_dataframe(df, self.language)

    def create_question_summary(self):
        chart_list = []
        questions_parameters = self.get_questions_parameters()
        for question in questions_parameters:
            question_title, question_type, position, has_custom_body = question
            charts = []
            chart_filter = Filter('=', 'position', position)
            question_name = f"{position}. {question_title}"
            if question_type in ["short_answer", "long_answer"]:
                chart = TableChart(question_name, self)
                chart.set_filters(chart_filter)
                chart.set_filters(Filter('!=', 'answer', 'Pas de réponse'))
                chart.set_fields(
                    Fields([{'name': 'answer', 'type': 'type/Text'}])
                )
                charts.append(chart)
            if question_type in ["single_option", "multiple_option"] and has_custom_body:
                custom_body_question_name = question_name + " (champ libre)"
                chart = TableChart(custom_body_question_name, self)
                chart.set_filters(chart_filter)
                chart.set_filters(Filter('!=', 'answer', 'Pas de réponse'))
                # TODO: find how to create a "not empty" filter (https://discourse.metabase.com/t/api-how-to-create-a-not-empty-filter/234624)
                #chart.set_filters(Filter('not-empty', 'custom_body', ''))
                chart.set_fields(
                    Fields([
                        {'name': 'answer', 'type': 'type/Text'},
                        {'name': 'custom_body', 'type': 'type/Text'}
                        ])
                )
                charts.append(chart)
            if question_type in ["single_option"]:
                chart = PieChart(question_name, self)
                chart.set_filters(chart_filter)
                chart.set_aggregation(
                    Aggregation(
                        ['count'],
                        Fields([{'name': 'answer', 'type': 'type/Text'}])
                    )
                )
                charts.append(chart)
            if question_type in ["multiple_option"]:
                chart = BarChart(question_name, self)
                chart.set_filters(chart_filter)
                chart.set_aggregation(
                    Aggregation(
                        ['count'],
                        Fields([{'name': 'answer', 'type': 'type/Text'}])
                    )
                )
                chart.set_order(Order('desc'))
                chart.set_custom_params(
                    [{
                        "name": "visualization_settings",
                        "value": {
                            'graph.x_axis.labels_enabled': False,
                            'graph.y_axis.labels_enabled': False
                        }
                    }]
                )
                charts.append(chart)
            if question_type in ["matrix_single", "matrix_multiple"]:
                chart = BarChart(question_name, self)
                chart.set_filters(chart_filter)
                chart.set_aggregation(
                    Aggregation(
                        ['count'],
                        Fields(
                            [
                                {
                                    'name': 'sub_matrix_question',
                                    'type': 'type/Text'
                                },
                                {'name': 'answer', 'type': 'type/Text'}
                            ]
                        )
                    )
                )
                chart.set_order(Order('desc'))
                chart.set_custom_params(
                    [{
                        "name": "visualization_settings",
                        "value": {
                            "graph.dimensions": [
                                "sub_matrix_question",
                                "answer"
                            ],
                            "graph.metrics": ["count"],
                            'graph.x_axis.labels_enabled': False,
                            'graph.y_axis.labels_enabled': False
                        }
                    }]
                )
                charts.append(chart)
            if question_type in ["files"]:
                chart = TableChart(question_name, self)
                chart.set_filters(chart_filter)
                chart.set_fields(
                    Fields(
                        [
                            {'name': 'answer', 'type': 'type/Text'},
                            {'name': 'custom_body', 'type': 'type/*'}
                        ]
                    )
                )
                charts.append(chart)
            if question_type in ["sorting"]:
                chart = HorizontalBarChart(question_name, self)
                chart.set_filters(chart_filter)
                chart.set_aggregation(
                    Aggregation(
                        [
                            'sum',
                            Fields(
                                [
                                    {
                                        'name': 'sorting_points',
                                        'type': 'type/Integer'
                                    }
                                ])],
                        Fields([{'name': 'answer', 'type': 'type/Text'}])
                    )
                )
                chart.set_order(Order('desc'))
                chart.set_custom_params(
                    [{
                        "name": "visualization_settings",
                        "value": {
                            'graph.x_axis.labels_enabled': False,
                            'graph.y_axis.labels_enabled': False
                        }
                    }]
                )
                charts.append(chart)
            for chart in charts:
                created_chart = chart.create_chart()
                chart_list.append([chart, created_chart])
        return chart_list
