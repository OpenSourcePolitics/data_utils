# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ```
#     _    ______     _____ ____ _____
#    / \  |  _ \ \   / /_ _/ ___| ____|  _
#   / _ \ | | | \ \ / / | | |   |  _|   (_)
#  / ___ \| |_| |\ V /  | | |___| |___   _
# /_/   \_\____/  \_/  |___\____|_____| (_)
# ```
#
# Use jupytext to edit this python script as a notebook.
# http://jupytext.readthedocs.io

# %%
import pandas as pd
import requests
from tqdm import tqdm
from itertools import count

# %% [markdown]
# **Step 1**: access the graphQL api of decidim.
# The decidim main endpoint is `https://citizens.ec.europa.eu/participation/`
# So the docs of the API are located in `https://citizens.ec.europa.eu/participation/api/docs`

# %%
URL = "https://citizens.ec.europa.eu/participation/api"


# %%
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


# %%
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

# %%
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

# %%
df = pd.DataFrame(processes["data"]["participatoryProcesses"])
df["title"] = [x["translation"] for x in df["title"]]
df

# %% [markdown]
# We will focus on MMF, intergenerational fairness, youth dialogues and assembly pollinators

# %%
current_processes = [
    ("mmf", 67, ),
    ("intergenerational-fairness", 100),
    ("youth-policy-dialogues", 68),
    ("young-citizens-assembly-pollinators",	133),
    ("tackling-hatred-in-society",	35)
]

# %% [markdown]
# Now, for the heavy lifting

# %%
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
              comments {
                id
                body
              }
              endorsements {
                id
              }
              createdAt
            }
          }
        }
      }
    }
  }
}
"""


def fetch_data(process_id):
    all_proposals = []
    after_cursor = None

    headers = {
        "Content-Type": "application/json"
    }

    for _ in tqdm(count()):
        json={'query': query, 'variables': {'id': process_id, 'after': after_cursor}}
        response = requests.post(URL, json=json, headers=headers)
        if response.status_code != 200:
            print(f"Query failed to run by returning code of {response.status_code}. {response.text}")
            return all_proposals


        response_json = response.json()
        if not('data' in response_json and response_json['data']['participatoryProcess']):
            print(f"Error in response JSON structure: {response_json}")
            return all_proposals

        data = response_json['data']['participatoryProcess']
        if not (data and 'components' in data and data['components']):
            print(f"No components found in process {process_id}. Full response: {response_json}")
            return all_proposals

        non_null_components = [x for x in data["components"] if x]

        if len(non_null_components) != 1:
            print(len(non_null_components))
            print("strange, list is not a singleton")
        proposals_data = non_null_components[0]['proposals']
        assert None not in proposals_data['edges']
        all_proposals.extend(proposals_data['edges'])
        page_info = proposals_data['pageInfo']
        if page_info['hasNextPage']:
            after_cursor = page_info['endCursor']
        else:
            return all_proposals

    return all_proposals

# %%
data = {}
for (name, p_id) in current_processes:
    print(f"extracting {name}")
    data[name] =  fetch_data(p_id)


# %%
def process_to_df(proposals):
    rows = []
    for edge in proposals:
        proposal = edge['node']
        if proposal is None:
            continue
        proposal_id = proposal['id']
        # Get the French translation if available
        title_translations = proposal['title']['translations']
        title = next((t['text'] for t in title_translations if t['locale'] == 'fr'),
                     "No title") if title_translations else "No title"
        comments = len(proposal['comments'])
        endorsements = len(proposal['endorsements'])
        created_at = proposal['createdAt']
        rows.append({
            #'Process': process_name,
            'Proposal ID': proposal_id,
            'Title': title,
            'Comments': comments,
            'Endorsements': endorsements,
            'Created At': created_at
        })

    return pd.DataFrame(rows)


# %%
for (name, _) in current_processes:
    result = process_to_df(data[name])
    print(result.describe())
    result.to_csv(f"data_2025/{name}.csv", index=False)

# %% [markdown]
# Janvier à Aout 2025
#
# Si possible aout à décembre

# %%
