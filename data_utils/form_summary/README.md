# Metabase Forms Summary Automation
This project aims to make a summary of a Decidim Form, based on models available on [this project](https://github.com/OpenSourcePolitics/metabase_automation/) and the [Metabase_API_python wrapper](https://github.com/vvaezian/metabase_api_python.git)

## Requirements
- [Poetry](https://python-poetry.org/)
- Having setup the answers' request using the SQL request available on the [decidim_cards repo]()
- Fill the `credentials.py` with :
    - Metabase credentials
    - ID of the base request
    - ID of the Decidim form
    - ID of the collection in which you want to have the created charts and dashboard

## Setup
1. Clone repository
2. Run `poetry install`
3. Run `poetry run make_summary`

## TODO
- [x] Connect to Metabase
- [x] Retrieve all forms with provided model ID
- [x] Retrieve specific form information
- [x] Retrieve all questions of specified form with their types and IDs
- [x] Create card that gathers answers of the specified question
    - [x] Short answers
    - [x] Long answers
    - [x] Single option
    - [x] Multiple option
    - [x] Sorting (cumulative points)
    - [x] Matrix simple
    - [x] Matrix multiple
    - [x] Files

### Improvements
- [ ] Retrieve automatically the models which contains the forms information
- [ ] Resize box of report dashboardcards to fill all width and a pre-determined height.
- [ ] Interactive creation that displays the question title and type to give choice of visualization
- [ ] Test cover : red, green, blue
- [ ] Give possibility to hide/show labels
- [ ] Pin created dashboard
- [ ] Message the consultant concerned by the form summary
- [ ] Order answers by number of occurences
