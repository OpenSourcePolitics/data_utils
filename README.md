# Data utils
This repository gathers all command-line tools and scripts we use at Open Source Politics to handle our work.

It aims is to gather all of our tools as **submodules**

## Requirements
- Python
- Poetry (see installation process [here](https://python-poetry.org/docs/#installation))

## Setup
1. Clone repository 
```bash
git clone git@github.com:OpenSourcePolitics/data_utils.git
```
2. Install dependencies : `poetry install`
3. Create a `.env` file from the `.env.example` and fill it with your credentials.
4. Source your env file
4. Follow instructions in the README of the specified repository

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

### form_automation
> Allows you to automatically all cards for a Decidim form on Metabase
- `poetry run form_summarize`

### file_import
> Allows you to send data directly to a Postgres database that is connected to Metabase
> ⚠️ Make sure the file you're importing is at the root of this project to be imported ⚠️
- `poetry run file_import`

## Aknowledgements
This repo would be nothing without the wrapper made by vvaezian accessible here:
[Metabase API Python](https://github.com/vvaezian/metabase_api_python/)

## Contribute
- [Create an issue](https://github.com/OpenSourcePolitics/data_utils/issues) to report a bug/ask for a new feature
- [Fork this project](https://github.com/OpenSourcePolitics/data_utils/issues) to make your changes and make a PR

## License
This software is licensed under the GNU AGPLv3, which states that **you can use, modify and redistribute this software as long as you publish the modifications under the same license.**
For more information, check [here](https://www.gnu.org/licenses/agpl-3.0.html)