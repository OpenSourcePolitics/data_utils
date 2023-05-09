# Data utils
This repository gathers all command-line tools and scripts we use at Open Source Politics to handle our work.

It currently contains 

## Requirements
1. Poetry (see installation process [here](https://python-poetry.org/docs/#installation))
2. Create a `.env` file from the `.env.example` provided with your credentials

### DB changer
> Allows you to dynamically change the database of any indicator
`poetry run db_changer`

### Model changer
> Allows you to dynamically change the model of any indicator
`poetry run model_changer`


## Aknowledgements
This repo would be nothing without the wrapper made by vvaezian accessible here:
[Metabase API Python](https://github.com/vvaezian/metabase_api_python/)