# Metabase Forms Summary Automation
This project aims to make a summary of a Decidim Form, based on models available on [this project](https://github.com/OpenSourcePolitics/metabase_automation/) and the [Metabase_API_python wrapper](https://github.com/vvaezian/metabase_api_python.git)

## Requirements
- [Poetry](https://python-poetry.org/)
- Having setup the answers' request using the SQL request available on the [decidim_cards repo]()

## Setup
`poetry run make_summary`

### Improvements
- [x] Retrieve automatically the models which contains the forms information
- [ ] Resize box of report dashboardcards to fill all width and a pre-determined height.
- [ ] Interactive creation that displays the question title and type to give choice of visualization
- [ ] Test cover : red, green, blue
- [ ] Give possibility to hide/show labels
- [x] Pin created dashboard
- [ ] Message the consultant concerned by the form summary
- [ ] Order answers by number of occurences