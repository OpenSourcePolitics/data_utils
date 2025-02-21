from .forms_summary import FormsSummary
from ..utils import (
    create_dashboard,
    add_cards_to_dashboard,
    get_customer_collection_id
)


def make_summary_dbt():
    customer_collection_name = input("Enter name of the customer collection: ")
    decidim_questionnaire_id = int(input("Enter ID of the Decidim form: "))
    database_id = int(input("Enter ID of the Database of the form: "))
    form_name = input("Enter name of the form (used for dashboard creation): ")

    collection_id = get_customer_collection_id(customer_collection_name)

    forms_parameters = {
        'DECIDIM_QUESTIONNAIRE_ID': decidim_questionnaire_id,
        'DATABASE_ID': database_id,
        'FORM_NAME': form_name,
        'COLLECTION_ID': collection_id
    }

    f = FormsSummary(forms_parameters=forms_parameters)
    f.get_questions_parameters()
    chart_list = f.create_question_summary()

    dashboard = create_dashboard(form_name, f.collection_id)
    add_cards_to_dashboard(dashboard, chart_list)
