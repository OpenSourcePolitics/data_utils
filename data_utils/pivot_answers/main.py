from data_utils.utils import (
    get_answer_model_id,
    MTB
)
import pandas as pd
import ast
from enum import Enum


FILENAME = 'data'
QUESTIONS_COLUMNS = ['question_title', 'question_type', 'position']
ANSWERS_COLUMNS = [
    'answer',
    'custom_body',
    'sorting_position',
    'session_token',
    'sub_matrix_question'
]
FOR_METABASE = True


class Category(Enum):
    SIMPLE = 1
    COMPLEX = 2
    SORTING = 3


class Question:
    def __init__(self, type, position, title, **kwargs):
        self.type = type
        self.position = position
        self.title = title

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.type in [
            'short_answer', 'long_answer', 'single_option', 'files'
        ]:
            self.category = Category.SIMPLE
        elif self.type in [
            'multiple_option', 'matrix_single', 'matrix_multiple'
        ]:
            self.category = Category.COMPLEX
            if self.type == 'multiple_option':
                self.filtering_column = 'answer'
                wanted_sub_columns = self.possible_answers
            else:
                self.filtering_column = 'sub_matrix_question'
                wanted_sub_columns = self.sub_affirmations
            self.sub_affirmations = [
                sub_affirmation.strip()
                for sub_affirmation
                in ast.literal_eval(wanted_sub_columns)
            ]
        elif self.type == 'sorting':
            self.category = Category.SORTING
            raise NotImplementedError("Not implemented")


# Recover answers data
def get_data(answer_model_id, questions_info_id, form_id):
    # Get answers data
    df = pd.DataFrame(MTB.get_card_data(card_id=answer_model_id))

    df.rename(
        columns={
            'Titre de la question': 'question_title',
            'Type de question': 'question_type',
            'Position': 'position',
            'Réponse': 'answer',
            'Corps personnalisé': 'custom_body',
            'Jeton de session': 'session_token',
            'Position de tri': 'sorting_position',
            # 'Points de tri': 'sorting_points',
            'Question sous-matricielle': 'sub_matrix_question',
            'ID du questionnaire': 'decidim_questionnaire_id'
        },
        inplace=True
    )

    df_answers = df[df.decidim_questionnaire_id == form_id]

    # Get questions info data
    df_questions_info = pd.DataFrame(
        MTB.get_card_data(card_id=questions_info_id)
    )
    df_questions_info = df_questions_info.rename(
        columns={
            'Titre de la question': 'question_title',
            'Type de question': 'question_type',
            'Position': 'position',
            'Réponse': 'answer',
            'Corps personnalisé': 'custom_body',
            'Jeton de session': 'session_token',
            'Position de tri': 'sorting_position',
            # 'Points de tri': 'sorting_points',
            'Question sous-matricielle': 'sub_matrix_question',
            'ID du questionnaire': 'questionnaire_id'
        }
    )

    df_questions_info = df_questions_info[
        [
            'position',
            'question_type',
            'question_title',
            'possible_answers',
            'sub_affirmations'
        ]
    ]

    return df_answers, df_questions_info


def pivot_answers(df_answers, df_questions_infos, for_metabase):
    # Final thing
    pivoted_answers = df_answers[['session_token']].drop_duplicates()

    # For each question, retrieve the dataframe with the relevant columns
    for index, question_infos in df_questions_infos.iterrows():
        question = Question(
            question_infos.question_type,
            question_infos.position,
            question_infos.question_title,
            possible_answers=question_infos.possible_answers,
            sub_affirmations=question_infos.sub_affirmations
        )

        df_answers_to_question = (
            df_answers[df_answers['position'] == question.position]
            [ANSWERS_COLUMNS]
        )

        pivoted_answers_to_question = pivot_answers_to_column(
            question,
            df_answers_to_question
        )

        pivoted_answers = pivoted_answers.merge(
            pivoted_answers_to_question,
            how='left',
            on='session_token'
        )

    return pivoted_answers


def get_or_create_questions_infos(client_name, questionnaire_id):
    card_name = f'Questions - Questionnaire {questionnaire_id}'
    try:
        questions_infos_id = MTB.get_item_id('card', card_name)
    except ValueError:
        print("Questions infos card not existing")

        db_id = MTB.get_item_id('database', client_name)
        request = open(
            './data_utils/pivot_answers/request.sql'
        ).read().replace('QUESTIONNAIRE_ID', str(questionnaire_id))
        questions_infos_id = MTB.create_card(
            custom_json={
                'name': card_name,
                'display': 'table',
                'dataset_query': {
                    'database': db_id,
                    'native': {'query': request},
                    'type': 'native',
                },
                'collection_id': MTB.get_item_id('collection', client_name)
            },
            return_card=True
        )['id']
    return questions_infos_id


def pivot_answers_to_column(question, df_answers_to_question):
    pivoted_answers_to_question = df_answers_to_question[
        ['session_token']
    ].drop_duplicates()

    if question.category == Category.SIMPLE:
        pivoted_answers_to_question = df_answers_to_question[
            ['session_token', 'answer']
        ]
        column_name = f'{question.position}. {question.title}'
        pivoted_answers_to_question = pivoted_answers_to_question.rename(
            columns={'answer': column_name}
        )
    elif question.category == Category.COMPLEX:
        for index, sub_affirmation in enumerate(question.sub_affirmations):
            column_name = (
                f'{question.position}. {question.title[:20]} -'
                f' {sub_affirmation}'
            )
            sub_affirmation_df = df_answers_to_question[
                df_answers_to_question[question.filtering_column]
                == sub_affirmation
            ][['session_token', 'answer']]

            # If matrix_multiple, concat all answers in single column
            if question.type == 'matrix_multiple':
                sub_affirmation_df = (
                    sub_affirmation_df
                    .set_index('session_token')
                    .groupby(['session_token'])
                    .transform(lambda x: ','.join(x))
                    .drop_duplicates()
                )

            sub_affirmation_df.rename(
                columns={'answer': column_name},
                inplace=True
            )

            if question.type == 'multiple_option':
                sub_affirmation_df[column_name] = (
                    sub_affirmation_df[column_name].apply(lambda x: 'Oui')
                )

            pivoted_answers_to_question = pivoted_answers_to_question.merge(
                sub_affirmation_df,
                how='left',
                on='session_token'
            )

    return pivoted_answers_to_question


def get_column_name(question):
    if question.category == Category.SIMPLE:
        return f'{question.position}. {question.title}'
    elif question.category == Category.COMPLEX:
        return None
    else:
        raise NotImplementedError("Not implemented")


def main():
    questionnaire_id = int(input("Enter ID of the targeted questionnaire: "))
    customer_name = input("Enter customer name: ")

    answer_model_id = get_answer_model_id(customer_name)
    questions_info_id = get_or_create_questions_infos(
        customer_name,
        questionnaire_id
    )
    for_metabase = True
    # (
    #     True if input("For Metabase of not ?[y/N]: ") == 'y' else False
    # )

    df, df_questions_info = get_data(
        answer_model_id,
        questions_info_id,
        questionnaire_id
    )
    final_df = pivot_answers(df, df_questions_info, for_metabase)
    final_df.to_csv('file.csv', index=False)
