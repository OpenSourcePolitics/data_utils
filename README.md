# Data utils
This repository gathers all command-line tools and scripts we use at Open Source Politics to handle our work.

It aims is to gather all of our tools as **submodules**

## Requirements
1. Poetry (see installation process [here](https://python-poetry.org/docs/#installation))
2. Create a `.env` file from the `.env.example` provided with your credentials

## Howto
1. Clone repository 
```bash
git clone git@github.com:OpenSourcePolitics/data_utils.git
```
2. Follow instructions in the README of the specified repository

## List of all available functionalities
Here's a list of all available functionalities. They are classed by folder.

### card_changer
> Allows you to dynamically change a specific attribute of a Metabase card. Knowledge of the card description is mandatory.

Three commands are available:
- `poetry run db_changer` : change the database of any card. Useful if your card is based on a model which database was switched.
- `poetry run model_changer` : change the model of any card. Requires that the provided card is a graphical one.
- `poetry run custom_changer` : allows chirurgical modification of a card if previous commands aren't consistent.

### query_checker
> Allows you to verify that all cards inside a specified collection are working.
- `poetry run query_checker`

## Aknowledgements
This repo would be nothing without the wrapper made by vvaezian accessible here:
[Metabase API Python](https://github.com/vvaezian/metabase_api_python/)