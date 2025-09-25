# ---
# jupyter:
#   jupytext:
#     formats: py:percent
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
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import HoverTool, Legend
from bokeh.layouts import column
from bokeh.models.formatters import DatetimeTickFormatter
output_notebook()

# %%
pd.read_csv("data_2025/mmf.csv")

# %%
date_format = "%Y-%m-%dT%H:%M:%S%z"


# %%
def load(file_path):
    result = pd.read_csv(file_path)
    result['Created At'] = pd.to_datetime(result['Created At'], errors='coerce', format=date_format, utc=True)
    result = result.dropna(subset=['Created At'])
    return result


# %%
load("data_2025/mmf.csv")

# %%
load("data_2025/intergenerational-fairness.csv")

# %%
load("data_2025/young-citizens-assembly-pollinators.csv")

# %%
load("data_2025/youth-policy-dialogues.csv")

# %%
# Group by date and count the number of proposals per day
proposals_per_day = df.groupby(df['Created At'].dt.date).size()

# Plot the evolution of the number of proposals
plt.figure(figsize=(10, 6))
plt.plot(proposals_per_day.index, proposals_per_day.values, marker='o', linestyle='-')
plt.title('Evolution of the Number of Proposals Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Proposals')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Display the plot
plt.show()


# %%
def display_cumulative_figure(df, title):
    # Grouper par date et calculer les statistiques journalières
    daily_propositions = df.groupby(df['Created At'].dt.date).size()
    daily_comments = df.groupby(df['Created At'].dt.date)['Comments'].sum()
    daily_endorsements = df.groupby(df['Created At'].dt.date)['Endorsements'].sum()

    # Créer un DataFrame avec toutes les statistiques
    daily_stats = pd.DataFrame({
        'Date': daily_propositions.index,
        'Propositions': daily_propositions.values,
        'Commentaires': daily_comments.values,
        'Endorsements': daily_endorsements.values
    })

    # Convertir la date en datetime pour Bokeh
    daily_stats['Date'] = pd.to_datetime(daily_stats['Date'])

    # Trier par date
    daily_stats = daily_stats.sort_values('Date')

    # Calculer les cumuls
    daily_stats['Propositions_cumul'] = daily_stats['Propositions'].cumsum()
    daily_stats['Commentaires_cumul'] = daily_stats['Commentaires'].cumsum()
    daily_stats['Endorsements_cumul'] = daily_stats['Endorsements'].cumsum()

    # Créer la visualisation Bokeh
    p = figure(
        title=title,
        x_axis_label="Date",
        y_axis_label="Cumulative count",
        x_axis_type="datetime",
        width=1000,
        height=600,
        toolbar_location="above"
    )

    # Ajouter les lignes
    line1 = p.line(daily_stats['Date'], daily_stats['Propositions_cumul'],
                   legend_label="Proposals", line_width=3, color="#1f77b4")
    line2 = p.line(daily_stats['Date'], daily_stats['Commentaires_cumul'],
                   legend_label="Comments", line_width=3, color="#ff7f0e")
    line3 = p.line(daily_stats['Date'], daily_stats['Endorsements_cumul'],
                   legend_label="Endorsements", line_width=3, color="#2ca02c")

    # Ajouter des cercles pour les points de données
    p.scatter(daily_stats['Date'], daily_stats['Propositions_cumul'],
             size=6, color="#1f77b4", alpha=0.7)
    p.scatter(daily_stats['Date'], daily_stats['Commentaires_cumul'],
             size=6, color="#ff7f0e", alpha=0.7)
    p.scatter(daily_stats['Date'], daily_stats['Endorsements_cumul'],
             size=6, color="#2ca02c", alpha=0.7)

    # Configurer les outils de survol
    hover = HoverTool(tooltips=[
        ("Date", "@x{%F}"),
        ("Valeur", "@y{0,0}")
    ], formatters={'@x': 'datetime'})

    p.add_tools(hover)

    # Configurer la légende
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.title.text_font_size = "16pt"
    return p


# %%
data = load("data_2025/mmf.csv")
show(display_cumulative_figure(data, "Multiannual financal framework"))

# %%
data = load("data_2025/youth-policy-dialogues.csv")
show(display_cumulative_figure(data, "Youth policy dialogues"))

# %%
data = load("data_2025/young-citizens-assembly-pollinators.csv")
show(display_cumulative_figure(data, "Pollinators"))

# %%
data = load("data_2025/intergenerational-fairness.csv")
show(display_cumulative_figure(data, "Intergenerational fairness"))

# %%
