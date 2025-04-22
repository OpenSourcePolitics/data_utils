from .forms_summary import FormsSummary
from ..utils import (
    create_dashboard,
    add_cards_to_dashboard,
    get_customer_collection_id,
    get_answer_model_id
)

def make_summary():
    customer_collection_name = input("Enter name of the customer collection: ")
    form_id = int(input("Enter ID of the Decidim form: "))
    form_name = input("Enter name of the form (used for dashboard creation): ")
    model_name = input("Enter name of the model created using make_form_filters (if any): ") or 'Réponses aux questionnaires'
    lang = (
        input("Enter language of the customer[fr/en; default is fr]: ") or 'fr'
    )

    collection_id = get_customer_collection_id(customer_collection_name)
    answer_model_id = get_answer_model_id(customer_collection_name)

    credentials = {
        'FORM_ID': form_id,
        'FORM_NAME': form_name,
        'ANSWERS_MODEL_ID': answer_model_id,
        'COLLECTION_ID': collection_id,
        'LANGUAGE': lang
    }
    f = FormsSummary(credentials=credentials)
    f.get_questions_parameters()

    chart_list = f.create_question_summary()
    dashboard = create_dashboard(form_name, f.collection_id)
    add_cards_to_dashboard(dashboard, chart_list)
