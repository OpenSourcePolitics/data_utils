# Metabase utils
Gathers commands used at Open Source Politics to manage Metabase indicators 
Allows data analyst to rapidly change a database of a Metabase indicator

## Requirements
1. Poetry installed 
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