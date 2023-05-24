from data_utils.utils import (
    parse_options,
    get_answer_model_id,
    MTB
)
import pandas as pd
import os


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
    df_questions_info.rename(
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
        },
        inplace=True
    )

    return df_answers, df_questions_info


def pivot_answers(df_answers, df_questions_info, for_metabase):
    import pdb; pdb.set_trace()
    questions_infos = df_questions_info[
        [
            'position',
            'question_type',
            'question_title',
            'possible_answers',
            'sub_affirmations'
        ]
    ]

    # Final thing
    pivoted_answers = df_answers[['session_token']].drop_duplicates()

    # For each question, retrieve the dataframe with the relevant columns
    for question_infos in questions_infos[['question_title']]:
        question_title, question_type, position = question_infos
        df_answers_to_question = df_answers[df_answers['position'] == position][ANSWERS_COLUMNS]

        pivoted_answers_to_question = pivot_answers_to_column(
            pivoted_answers[['session_token']],
            question_infos,
            df_answers_to_question
        )
            
        pivoted_answers = pivoted_answers.merge(
            pivoted_answers_to_question,
            how='left',
            on='session_token'
        )
        pdb.set_trace()
        elif question_type in ['multiple_option']:
            extraction = (
                df_questions_info[
                    df_questions_info['position'] == position
                ]['possible_answers']
            )
            options = parse_options(extraction)
            for option in options:
                option_checked_df = filtered_df[
                    filtered_df['answer'].str.contains(option)
                ]
                if for_metabase:
                    answer_column = (
                        f'{position}. {question_title[:30]} {option[:25]}'
                    )
                else:
                    f'{position}. {question_title} {option}'
                final_df[answer_column] = None
                for index, row in option_checked_df.iterrows():
                    mask = final_df['session_token'].str.contains(
                        row['session_token']
                    )
                    final_df.loc[mask, answer_column] = (
                        row.custom_body or 'Oui'
                    )
        # elif question_type in ['matrix_single']:
        #     extraction = (
        #         df_questions_info[
        #             df_questions_info['position'] == position
        #         ]['sub_affirmations']
        #     )
        #     sub_affirmations = parse_options(extraction)
        #     for sub_affirmation in sub_affirmations:
        #         sub_affirmation_checked = filtered_df[
        #             filtered_df['sub_matrix_question'] == sub_affirmation
        #         ]
        #         if for_metabase:
        #             answer_column = (
        #                 f'{position}. {question_title[:30]} '
        #                 f'{sub_affirmation[:25]}'
        #             )
        #         else:
        #             f'{position}. {question_title} {sub_affirmation}'
        #         final_df[answer_column] = None
        #         for index, row in sub_affirmation_checked.iterrows():
        #             mask = final_df['session_token'].str.contains(
        #                 row['session_token']
        #             )
        #             final_df.loc[mask, answer_column] = row['answer']
        # elif question_type in ['sorting']:
        #     extraction = df_questions_info[
        #         df_questions_info['position'] == position
        #     ]
        #     sorting_length = extraction[['sorting_length']].values[0][0]
        #     for i in range(sorting_length):
        #         if for_metabase:
        #             answer_column = (
        #                 f'{position}. {question_title[:40]} - Position {i}'
        #             )
        #         else:
        #             answer_column = (
        #                 f'{position}. {question_title} - Position {i}'
        #             )
        #         final_df[answer_column] = None
        #     for index, row in filtered_df.iterrows():
        #         if for_metabase:
        #             answer_column = (
        #                 f'{position}. {question_title[:40]}'
        #                 ' - '
        #                 f'Position {row["sorting_position"]}'
        #             )
        #         else:
        #             answer_column = (
        #                 f'{position}. {question_title}'
        #                 ' - '
        #                 f'Position {row["sorting_position"]}'
        #             )
        #         mask = final_df['session_token'].str.contains(
        #             row['session_token']
        #         )
        #         final_df.loc[mask, answer_column] = row['answer']
        # elif question_type in ['matrix_multiple']:
        #     import pdb; pdb.set_trace()
        #     extraction = (
        #         df_questions_info[
        #             df_questions_info['position'] == position
        #         ]['sub_affirmations']
        #     )
        #     for index, row in filtered_df():
                
        #     sub_affirmations = parse_options(extraction)
        #     for sub_affirmation in sub_affirmations:
        #         sub_affirmation_checked = filtered_df[
        #             filtered_df['sub_matrix_question'] == sub_affirmation
        #         ]
        #         if for_metabase:
        #             answer_column = (
        #                 f'{position}. {question_title[:30]} '
        #                 f'{sub_affirmation[:25]}'
        #             )
        #         else:
        #             f'{position}. {question_title} {sub_affirmation}'
        #         final_df[answer_column] = None
        #         for index, row in sub_affirmation_checked.iterrows():
        #             mask = final_df['session_token'].str.contains(
        #                 row['session_token']
        #             )
        #             final_df.loc[mask, answer_column] = row['answer']                
        # else:
        #     raise NotImplementedError(
        #         f"This question type is not implemented yet {question_type}"
        #     )
    return pivoted_answers

def get_or_create_questions_infos(client_name, questionnaire_id):
    card_name = f'Questions - Questionnaire {questionnaire_id}'
    try:
        questions_infos_id = MTB.get_item_id('card', card_name)
    except ValueError:
        print("Questions infos card not existing")

        db_id = MTB.get_item_id('database', client_name)
        questions_infos_id = MTB.create_card(
            custom_json={
                'name': card_name,
                'display': 'table',
                'dataset_query': {
                    'database': db_id,
                    'native': {
                        'query': open(
                            './data_utils/pivot_answers/request.sql',
                            'r'
                        ).read().replace(
                            'QUESTIONNAIRE_ID',
                            str(questionnaire_id)
                        )
                    },
                    'type': 'native',
                },
                'collection_id': MTB.get_item_id('collection', client_name)
            },
            return_card=True
        )['id']
    return questions_infos_id
    

def pivot_answers_to_column(list_of_answerers, question_informations, df_answers_to_question):
    pivoted_answers_to_question = list_of_answerers
    question_title, question_type, position = question_informations
    if question_type in ['short_answer', 'long_answer', 'single_option','files']:
        pivoted_answers_to_question = df_answers_to_question[['session_token', 'answer']]
        column_name = f'{position}. {question_title}'
        pivoted_answers_to_question.rename(
            columns={'answer':column_name},
            inplace=True
        )
    elif question_type in ['multiple_option']:
        pivoted_answers_to_question
    # elif question_type in ['matrix_single']:
    #     pass
    # elif question_type in ['matrix_multiple']:
    #     pass
    else:
        print('not implemented yet')
        # raise NotImplementedError(f"Not implemented yet: {question_type}")

    return pivoted_answers_to_question


def get_column_name(question_informations):
    question_title, question_type, position = question_informations
    if question_type in ['short_answer', 'long_answer', 'single_option','files']:
        return f'{position}. {question_title}'
    # elif question_type in ['multiple_option']:

def main():
    questionnaire_id = int(input("Enter ID of the targeted questionnaire: "))
    customer_name = input("Enter customer name: ")

    answer_model_id = get_answer_model_id(customer_name)
    questions_info_id = get_or_create_questions_infos(customer_name, questionnaire_id)
    for_metabase = True if input("For Metabase of not ?[y/N]: ") == 'y' else False

    df, df_questions_info = get_data(answer_model_id, questions_info_id, questionnaire_id)
    final_df = pivot_answers(df, df_questions_info, for_metabase)
    final_df.to_csv('file.csv', index=False)
