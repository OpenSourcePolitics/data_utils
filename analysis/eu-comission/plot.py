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
import polars as pl
import bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource
from bokeh.transform import dodge
import datetime

output_notebook()

# %%
date_format = "%Y-%m-%dT%H:%M:%S%z"


# %%
def load(file_path):
    result = pl.read_csv(file_path)
    result = result.with_columns(pl.col("Date").str.to_datetime(time_zone="UTC"))
    assert not result["Date"].is_null().any()
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
def display_cumulative_figure(df, title, show_endorsements=True):
    """
    Affiche un graphique cumulatif des propositions, commentaires et endorsements.

    Args:
        df: DataFrame Polars contenant les données
        title: Titre du graphique

    Returns:
        Objet figure Bokeh
    """
    # Compter les entrées par type et par date
    proposals = (
        df.filter(pl.col("Type") == "PROPOSAL")
        .group_by("Date")
        .len()
        .rename({"len": "Proposals"})
        .sort("Date")
    )

    comments = (
        df.filter(pl.col("Type") == "COMMENT")
        .group_by("Date")
        .len()
        .rename({"len": "Comments"})
        .sort("Date")
    )

    endorsements = (
        df.filter(pl.col("Type") == "ENDORSEMENT")
        .group_by("Date")
        .len()
        .rename({"len": "Endorsements"})
        .sort("Date")
    )

    # Créer une liste complète de dates
    all_dates = (
        pl.concat(
            [
                proposals.select("Date"),
                comments.select("Date"),
                endorsements.select("Date"),
            ]
        )
        .unique()
        .sort("Date")
    )

    # Joindre les données et remplir les valeurs manquantes avec 0
    daily_stats = (
        all_dates.join(proposals, on="Date", how="left")
        .join(comments, on="Date", how="left")
        .join(endorsements, on="Date", how="left")
        .fill_null(0)
        .sort("Date")
    )

    # Calculer les cumuls
    daily_stats = daily_stats.with_columns(
        [
            pl.col("Proposals").cum_sum().alias("Proposals_cumul"),
            pl.col("Comments").cum_sum().alias("Comments_cumul"),
            pl.col("Endorsements").cum_sum().alias("Endorsements_cumul"),
        ]
    )

    daily_stats = daily_stats.with_columns(
        pl.col("Date").dt.convert_time_zone("Europe/Paris")
    )

    # Créer la visualisation Bokeh
    p = figure(
        title=title,
        x_axis_label="Date",
        y_axis_label="Cumulative count",
        x_axis_type="datetime",
        width=1200,
        height=600,
        toolbar_location="above",
    )

    # Ajouter les lignes
    line1 = p.line(
        daily_stats["Date"],
        daily_stats["Proposals_cumul"],
        legend_label="Proposals",
        line_width=3,
        color="#1f77b4",
    )

    line2 = p.line(
        daily_stats["Date"],
        daily_stats["Comments_cumul"],
        legend_label="Comments",
        line_width=3,
        color="#ff7f0e",
    )

    if show_endorsements:
        line3 = p.line(
            daily_stats["Date"],
            daily_stats["Endorsements_cumul"],
            legend_label="Endorsements",
            line_width=3,
            color="#2ca02c",
        )

    # Ajouter des cercles pour les points de données
    p.scatter(
        daily_stats["Date"],
        daily_stats["Proposals_cumul"],
        size=6,
        color="#1f77b4",
        alpha=0.7,
    )

    p.scatter(
        daily_stats["Date"],
        daily_stats["Comments_cumul"],
        size=6,
        color="#ff7f0e",
        alpha=0.7,
    )

    if show_endorsements:
        p.scatter(
            daily_stats["Date"],
            daily_stats["Endorsements_cumul"],
            size=6,
            color="#2ca02c",
            alpha=0.7,
        )

    DAY = 24 * 3600 * 1000

    # reglage pour afficher les graduations toutes les semaines ou tous les mois.
    # FIXME: il semble qu'il s'agisse d'un bug dans la librairie:
    # voir https://github.com/bokeh/bokeh/issues/14657

    # p.xaxis.ticker = bokeh.models.DatetimeTicker(
    #    #desired_num_ticks=12,
    #    tickers=[
    #        bokeh.models.AdaptiveTicker(base=DAY, mantissas=[7], num_minor_ticks=0),  # Par semaine
    #        bokeh.models.MonthsTicker(months=list(range(1, 13)))   # Par mois
    #    ]
    # )

    p.xaxis.ticker = bokeh.models.DatetimeTicker(desired_num_ticks=20)

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    if p.title:
        p.title.text_font_size = "16pt"

    return p


# %%
data = load("data_2025/mmf.csv")
show(display_cumulative_figure(data, "A new European budget fit for our ambitions"))

# %%
data = load("data_2025/youth-policy-dialogues.csv")
show(display_cumulative_figure(data, "Youth Policy Dialogues", show_endorsements=False))

# %%
data = load("data_2025/young-citizens-assembly-pollinators.csv")
show(display_cumulative_figure(data, "Young Citizens Assembly on Pollinators"))

# %%
data = load("data_2025/intergenerational-fairness.csv")
show(display_cumulative_figure(data, "Intergenerational Fairness"))

# %%
data = load("data_2025/tackling-hatred-in-society.csv")
# we want only the part after july 2024
data = data.filter(pl.col("Date").dt.date() > datetime.date(2024, 7, 1))
show(
    display_cumulative_figure(
        data, "Tackling Hatred in Society", show_endorsements=False
    )
)

# %%
df = load("data_2025/youth-policy-dialogues.csv")

# Grouper par date et compter par type
proposals_per_day = (
    df.filter(pl.col("Type") == "PROPOSAL")
    .group_by(pl.col("Date").dt.date())
    .len()
    .rename({"Date": "date", "len": "Propositions"})
)

comments_per_day = (
    df.filter(pl.col("Type") == "COMMENT")
    .group_by(pl.col("Date").dt.date())
    .len()
    .rename({"Date": "date", "len": "Commentaires"})
)

endorsements_per_day = (
    df.filter(pl.col("Type") == "ENDORSEMENT")
    .group_by(pl.col("Date").dt.date())
    .len()
    .rename({"Date": "date", "len": "Endorsements"})
)

# Créer une liste de toutes les dates uniques
all_dates = (
    pl.concat(
        [
            proposals_per_day.select("date"),
        ]
    )
    .unique()
    .sort("date")
)

# Initialiser le DataFrame final avec toutes les dates
daily_stats = all_dates

# Joindre les données par type
daily_stats = (
    daily_stats.join(proposals_per_day, on="date", how="left")
    .join(endorsements_per_day, on="date", how="left")
    .fill_null(0)
)

# Formater les dates pour l'affichage
daily_stats = daily_stats.with_columns(
    pl.col("date").dt.strftime("%b %Y").alias("Date_str"),
    pl.col("date").dt.strftime("%Y-%m-%d").alias("date_formatted"),
)

# Créer une source de données pour Bokeh
source = ColumnDataSource(daily_stats.to_dict(as_series=False))

# Créer la figure
p = figure(
    x_range=daily_stats["Date_str"].unique().to_list(),
    title="Youth Policy Dialogues - Statistics by period",
    x_axis_label="Date",
    y_axis_label="Count per period",
    width=800,
    height=600,
    toolbar_location="above",
)

# Largeur des barres
bar_width = 0.25

# Ajouter les rectangles (barres) avec décalage pour les grouper
p.vbar(
    x=dodge("Date_str", -bar_width / 2, range=p.x_range),
    top="Propositions",
    width=bar_width,
    source=source,
    color="#1f77b4",
    legend_label="Propositions",
    alpha=0.8,
)

p.vbar(
    x=dodge("Date_str", bar_width / 2, range=p.x_range),
    top="Endorsements",
    width=bar_width,
    source=source,
    color="#2ca02c",
    legend_label="Endorsements",
    alpha=0.8,
)


# Configurer la légende
p.legend.location = "top_right"
p.legend.click_policy = "hide"

if p.title:
    p.title.text_font_size = "16pt"
p.xaxis.axis_label_text_font_size = "12pt"
p.yaxis.axis_label_text_font_size = "12pt"
p.xaxis.major_label_orientation = 0.9

show(p)

# %%

# %%
