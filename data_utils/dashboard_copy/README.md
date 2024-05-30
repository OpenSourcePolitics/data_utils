# Dashboard copy
The goal of this script is to be able to : 
* first copy a dashboard to another collection 
* then to update each card in the dashboard to use another source database

The copy of the dashboard is done using the dashboard copy API endpoint.

The update of the source database is done using the card update API endpoint. 
To do so we need to: 
* Get the list of dashcards in the dashboard by calling the get dashboard API endpoint
* Then we filter only the dashcards that needs to be updated : those which contain an actual card
* For each card, we need to update the the database id, the tables ids, and the fields ids

## Limitations
- The script is not currently designed to work with : 
  - dashboards with cards that have multiple databases as sources (eg : one card uses data from the Lyon database and another one uses data from Angers database) 
  - cards that use Metabase Models as data source

## How to 
1. Before running script
    - Source the main `.env` file at the root of `data_utils` (cf. [README at the root of project](./../../README.md))
    - Get the *id of the dashboard* you wish to copy
    - Get the *id of the collection* you wish to copy it to
2. Run `poetry run dashboard_copy`
3. Once you copied the dashboard
    - Get the *id of the dashboard* you just copied 
    - Get the *id of the database* you want your dashboard to use as source database
    - Get the database schema you want to use : Usually 'prod' or 'dev'
4. Run `poetry run replace_dashboard_source_db` 🎉


## Possible improvements 
- Some work could be done to limit the api calls to Metabase
  - The script currently calls the Metabase API for each occurence of any field it needs to replace, a cache system could be added to avoid calling the API when the useful data previously has been retrieved
- Add more logging
- Handling