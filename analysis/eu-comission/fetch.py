import marimo

__generated_with = "0.16.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import requests
    from tqdm import tqdm
    return mo, pl, requests, tqdm


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ```
        _    ______     _____ ____ _____
       / \  |  _ \ \   / /_ _/ ___| ____|  _
      / _ \ | | | \ \ / / | | |   |  _|   (_)
     / ___ \| |_| |\ V /  | | |___| |___   _
    /_/   \_\____/  \_/  |___\____|_____| (_)
    ```


    This is a [marimo](https://marimo.io) notebook.
    To edit it in the web interface, run `marimo edit eu-comission/fetch.py`
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    **Step 1**: access the graphQL api of decidim.
    The decidim main endpoint is `https://citizens.ec.europa.eu/participation/`
    So the docs of the API are located in `https://citizens.ec.europa.eu/participation/api/docs`
    """
    )
    return


@app.cell
def _():
    URL = "https://citizens.ec.europa.eu/participation/api"
    return (URL,)


@app.cell
def _(URL, requests):
    # graphql request
    def gr(query):
        headers = {
            "Content-Type": "application/json"
        }

        json_msg = {
            "query": query,
        }

        response = requests.post(URL, headers=headers, json=json_msg)
        return response.json()
    return (gr,)


@app.cell
def _(gr):
    # list of all the past processes
    processes = gr(
    """
    {
      participatoryProcesses(filter: {publishedSince: "2018-01-01"}, order: {publishedAt: "asc"}) {
        slug
        id
        endDate
        title {
          translation(locale: "en")
        }
      }
    }
    """
    )
    processes
    return (processes,)


@app.cell
def _(gr):
    # account information
    gr(
    """
    {
      metrics(names:["users"]) {
        name
        count
        history { key value }
      }
    }
    """
    )
    return


@app.cell
def _(pl, processes):
    _df = pl.DataFrame(processes['data']['participatoryProcesses'])
    _df = _df.with_columns(title=pl.col('title').map_elements(lambda x: x['translation']))
    _df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""We will focus on MMF, intergenerational fairness, youth dialogues and assembly pollinators""")
    return


@app.cell
def _():
    current_processes = [
        ("mmf", 67, ),
        ("intergenerational-fairness", 100),
        ("youth-policy-dialogues", 68),
        ("young-citizens-assembly-pollinators",	133),
        ("tackling-hatred-in-society",	35)
    ]
    return (current_processes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Now, for the heavy lifting""")
    return


@app.cell
def _(URL, requests):
    query = """
    query getProcessData($id: ID!, $after: String) {
      participatoryProcess(id: $id) {
        components {
          ... on Proposals {
            proposals(first: 100, after: $after) {
              pageInfo {
                endCursor
                hasNextPage
              }
              edges {
                node {
                  id
                  title {
                    translations {
                      locale
                      text
                    }
                  }
                  body {
                  	translations {
                      locale
                      text
                    }
                  }
                  comments {
                    id
                    body
                    createdAt
                  }
                  endorsements {
                    id
                  }
                  createdAt
                  updatedAt
                }
              }
            }
          }
        }
      }
    }
    """

    def fetch_all_proposals(process_id):
        after_cursor = None

        headers = {
            "Content-Type": "application/json"
        }


        while True:
            json={'query': query, 'variables': {'id': process_id, 'after': after_cursor}}
            response = requests.post(URL, json=json, headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Query failed to run by returning code of {response.status_code}. {response.text}")


            response_json = response.json()
            if not('data' in response_json and response_json['data']['participatoryProcess']):
                raise ValueError(f"Error in response JSON structure: {response_json}")

            data = response_json['data']['participatoryProcess']
            if not (data and 'components' in data and data['components']):
                print(f"No components found in process {process_id}. Full response: {response_json}")
                continue

            non_null_components = [x for x in data["components"] if x]

            if len(non_null_components) != 1:
                print(len(non_null_components))
                print("strange, list is not a singleton")
            proposals_data = non_null_components[0]['proposals']
            assert None not in proposals_data['edges']
            for edge in proposals_data['edges']:
                if edge["node"] is None:
                    continue
                proposal = edge["node"]
                yield proposal

            page_info = proposals_data['pageInfo']
            if page_info['hasNextPage']:
                after_cursor = page_info['endCursor']
            else:
                return
    return (fetch_all_proposals,)


@app.cell
def _(fetch_all_proposals, tqdm):
    def get_text(element, default, lang="fr"):
        if not element["translations"]:
            return default
        translations = element['translations']
        title = next(
            (t['text'] for t in translations if t['locale'] == lang),
             default
        )
        return title

    def fetch_data(process_id):
         # this table will contain records of all events that occur in the platform:
        #  - proposal creation
        #  - votes
        #  - new comments
        # 
        # the type of an event can be either PROPOSAL, COMMENT or ENDORSEMENT
        result = []

        for proposal in tqdm(fetch_all_proposals(process_id)):
            title = get_text(proposal["title"], "[No title]")
            content = get_text(proposal["body"], "")

            proposal_id = proposal["id"]
            result.append(
                {
                    "Type": "PROPOSAL",
                    "Proposal_ID": proposal_id,
                    "Proposal_Title": title,
                    "Date": proposal["createdAt"],
                    "Content": content,
                }
            )
            for comment in proposal["comments"]:
                result.append(
                    {
                        "Type": "COMMENT",
                        "Proposal_ID": proposal_id,
                        "Proposal_Title": title,
                        "Date": comment["createdAt"],
                        "Content": comment["body"]
                    }
                )
            for endorsement in proposal["endorsements"]:
                result.append(
                    {
                        "Type": "ENDORSEMENT",
                        "Proposal_ID": proposal_id,
                        "Proposal_Title": title,
                        # IMPORTANT: we can't get the endorsement creation dates from the API,
                        # so we will consider they are created when the proposal is.
                        "Date": proposal["createdAt"],
                    }
                )
        return result
    return (fetch_data,)


@app.cell
def _(current_processes, fetch_data, pl):
    data = {}
    for _name, p_id in current_processes:
        print(f'extracting {_name}')
        data[_name] = pl.DataFrame(fetch_data(p_id))
    return (data,)


@app.cell
def _(current_processes, data, pl):
    for _name, _ in current_processes:
        _df = data[_name]
        _df = _df.with_columns(pl.col('Date').str.to_datetime('%Y-%m-%dT%H:%M:%S%z'))
        print(f'dataset `{_name}`:')
        print(_df.head())
        _df.write_csv(f'eu-comission/data_2025/{_name}.csv')
    return


@app.cell
def _(data):
    list(data.values())[0]
    return


@app.cell
def _(data):
    data["youth-policy-dialogues"]
    return


if __name__ == "__main__":
    app.run()
