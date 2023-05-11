# file_import
Purpose of this project is to provide a simple way to send data from a local data file to a database already linked in Metabase.

## Particular 
Requirements : 
- [**Python 3**](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org) (TL;DR run `curl -sSL https://install.python-poetry.org | python3 -` should work)

1. Clone and setup repository :
```python
git clone https://github.com/OpenSourcePolitics/metabase_file_import.git
cd metabase_file_import
poetry install
cp metabase_file_import/config-example.py metabase_file_import/config.py
```
2. Complete the `config.py` file with database informations
3. `poetry run main`
4. Follow instructions



