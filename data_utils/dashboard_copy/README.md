# Dashboard copy
The goal of this script is to be able to : 
* first copy a dashboard to another collection 
* then to update each card in the dashboard to use another source database

The copy of the dashboard is done using the dashboard copy API endpoint.
It is the easy part. 

The update of the source database is done using the card update API endpoint. 
To do so we need to: 
* Get the list of cards in the dashboard by calling the get dashboard API endpoint
* Then we filter only the cards that needs to be updated : those with a source database id and a source table id
* For each card, we need to update the database_id, the source_table_id and the field_ids
* To get those, we need to call different API endpoints to match the ids


## How to 
1. Before running script
    - Source the main `.env` file at the root of `data_utils` (cf. [README at the root of project](./../../README.md))
    - Get the id of the dashboard you wish to copy and the id of the collection you wish to copy it to
    - Once you copied the dashboard, get the id of the dashboard you just copied 
    - Get the id of the database you want your dashboard to use as source database
2. Run script 🎉
```bash
poetry run dashboard_copy
poetry run replace_dashboard_source_db
```


## TODO
- [ ] Update the dashboard to make the filters work
- [ ] Add better error handling
- [ ] Check if the replace_dashboard_source_db script works with cards that use joins

