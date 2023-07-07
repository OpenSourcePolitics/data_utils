# file_import
Purpose of this project is to provide a simple way to send data from a local data file to a database already linked in Metabase.

## Howto 
1. Before running script
    - Source the main `.env` file at the root of `data_utils` (cf. [README at the root of project](./../../README.md))
    - Copy and fill correctly the `.env` of this folder following `.env.example`
    - Source both files : `source .env && source data_utils/ls_import/.env`
2. Run script 🎉
```bash
poetry run ls_import
```



