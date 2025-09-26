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
from bokeh.models import HoverTool, Legend, ColumnDataSource, DaysTicker
from bokeh.layouts import column
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.transform import dodge
from bokeh.models import DatetimeTicker
from bokeh.core.enums import DatetimeUnits
import datetime
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

    TICKERS = [
        DaysTicker(days=[7])
    ]
    p.xaxis.ticker.tickers = TICKERS
    p.xaxis.ticker = DatetimeTicker(
        desired_num_ticks=20,  # Tous les 7 jours
        #unit=DatetimeUnits.days
    )

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
show(display_cumulative_figure(data, "A new European budget fit for our ambitions"))

# %%
data = load("data_2025/youth-policy-dialogues.csv")
show(display_cumulative_figure(data, "Youth Policy Dialogues"))

# %%
data = load("data_2025/young-citizens-assembly-pollinators.csv")
show(display_cumulative_figure(data, "Young Citizens Assembly on Pollinators"))

# %%
data = load("data_2025/intergenerational-fairness.csv")
show(display_cumulative_figure(data, "Intergenerational Fairness"))

# %%
data = load("data_2025/tackling-hatred-in-society.csv")
# we want only the part after july 2024
data = data[data["Created At"].dt.date > datetime.date(2024, 7, 1)]
show(display_cumulative_figure(data, "Tackling Hatred in Society"))

# %%
df = load("data_2025/youth-policy-dialogues.csv")
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

# Convertir les dates en chaînes pour l'axe des x
daily_stats['Date_str'] = pd.to_datetime(daily_stats['Date']).dt.strftime('%B %Y')

# Créer une source de données pour Bokeh
source = ColumnDataSource(daily_stats)

# Créer la figure
p = figure(
    x_range=daily_stats['Date_str'].tolist(),
    title="Youth Policy Dialogues",
    x_axis_label="Date",
    y_axis_label="Number at each date",
    width=800,
    height=600,
    toolbar_location="above"
)

# Largeur des barres
bar_width = 0.25

# Ajouter les rectangles (barres) avec décalage pour les grouper
p.vbar(x=dodge('Date_str', -bar_width, range=p.x_range), 
               top='Propositions', 
               width=bar_width, 
               source=source,
               color="#1f77b4", 
               legend_label="Propositions",
               alpha=0.8)

p.vbar(x=dodge('Date_str', 0.0, range=p.x_range), 
               top='Commentaires', 
               width=bar_width, 
               source=source,
               color="#ff7f0e", 
               legend_label="Commentaires",
               alpha=0.8)

p.vbar(x=dodge('Date_str', bar_width, range=p.x_range), 
               top='Endorsements', 
               width=bar_width, 
               source=source,
               color="#2ca02c", 
               legend_label="Endorsements",
               alpha=0.8)

# Configurer les outils de survol
hover = HoverTool(tooltips=[
    ("Date", "@Date_str"),
    ("Propositions", "@Propositions"),
    ("Commentaires", "@Commentaires"),
    ("Endorsements", "@Endorsements")
])

p.add_tools(hover)

# Configurer la légende
p.legend.location = "top_right"
p.legend.click_policy = "hide"

# Améliorer l'apparence
p.title.text_font_size = "16pt"
p.xaxis.axis_label_text_font_size = "12pt"
p.yaxis.axis_label_text_font_size = "12pt"


# Afficher le graphique
show(p)

# %%
