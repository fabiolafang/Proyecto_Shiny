import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import json

from shinywidgets import output_widget, render_plotly
from shiny import App, render, ui, reactive
from shinywidgets import render_plotly

# =========================================================
#                 CARGA DE DATOS
# =========================================================

df = pd.read_excel("base_completa.xlsx")
df = df.replace({pd.NA: None, np.nan: None})

# Paleta pastel personalizada (la misma que usas)
custom_palette = [
    '#f1e3a0',
    '#f1d99a',
    '#f2cf93',
    '#f1c58d',
    '#f0ba8a',
    '#eeb087',
    '#eca685',
    '#e89c85',
    '#e49386',
    '#df8988',
    '#d9828a',
    '#d07a8c',
    '#c9738f',
    '#bf6c92',
    '#b36795',
    '#a66298',
    '#995e9c',
    '#885a9d',
    '#76589e',
    '#65559f'
]


# =========================================================
#             GRÁFICO 1: SCATTERPLOT
# =========================================================

def grafico_scatter():
    generos_unicos = df["genre_random"].dropna().unique()
    color_map = {gen: custom_palette[i % len(custom_palette)] for i, gen in enumerate(generos_unicos)}

    fig = px.scatter(
        df,
        x="budget_mill",
        y="revenue_mill",
        title="Relación entre Presupuesto y Ganancia",
        color="genre_random",
        size="popularity",
        hover_data=["title", "language_adj"],
        opacity=0.9,
        color_discrete_map=color_map
    )

    fig.update_layout(
        title_x=0.5,
        title_font=dict(size=22, color="black", family="Arial Black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_font=dict(size=14, color="black", family="Arial Black"),
        legend_font=dict(size=12, color="black"),
        legend=dict(bgcolor="rgba(255,255,255,0.6)"),
        xaxis=dict(showgrid=True, gridcolor="lightgray", tickfont=dict(size=13), title_font=dict(size=16)),
        yaxis=dict(showgrid=True, gridcolor="lightgray", tickfont=dict(size=13), title_font=dict(size=16))
    )

    return fig


# =========================================================
#               GRÁFICO 2: MAPA
# =========================================================

def grafico_mapa():
    df["country_random"] = df["country_random"].astype(str)

    mapa = gpd.read_file("naturalearth_countries/ne_110m_admin_0_countries.shp")

    conteo = df.groupby("country_random").size().reset_index(name="conteo")

    mapa_final = mapa.merge(conteo, left_on="ADMIN", right_on="country_random", how="left")
    mapa_final["conteo"] = mapa_final["conteo"].fillna(0)

    geojson_data = json.loads(mapa_final.to_json())

    fig = px.choropleth(
        mapa_final,
        geojson=geojson_data,
        locations=mapa_final.index,
        color="conteo",
        hover_name="ADMIN",
        color_continuous_scale="Sunset",
        title="Cantidad de películas por país",
    )

    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_coloraxes(
        cmin=0,
        cmax=100,
        colorbar=dict(
            ticks="outside",
            tickvals=list(range(0, 110, 10)),
            ticktext=[str(v) for v in range(0, 110, 10)]
        )
    )

    fig.update_layout(
        title_x=0.5,
        title_font=dict(size=22, family="Arial Black"),
        margin={"r":0, "t":30, "l":0, "b":0}
    )

    return fig


# =========================================================
#         GRÁFICO 3: FRECUENCIA (HISTOGRAMAS)
# =========================================================

def grafico_histogramas(var):
    generos = df["genre_random"].dropna().unique()

    fig = go.Figure([
        go.Histogram(
            x=df.loc[df["genre_random"] == gen, var],
            name=gen,
            visible=(i == 0),
            opacity=1,
            marker_color=custom_palette[i % len(custom_palette)]
        )
        for i, gen in enumerate(generos)
    ])

    steps = [dict(method="restyle", args=[{"nbinsx": b}], label=str(b)) for b in range(10, 110, 10)]

    bins_slider = [dict(active=2, steps=steps, currentvalue={"prefix": "Bins: "})]

    buttons = []
    for i, gen in enumerate(generos):
        visibility = [False] * len(generos)
        visibility[i] = True
        buttons.append(dict(label=gen, method="update", args=[{"visible": visibility}]))

    dropdown_menu = [
        dict(buttons=buttons, direction="down", showactive=True, x=1.15, y=1)
    ]

    fig.update_layout(
        title=f"Distribución de {var} por Género",
        title_x=0.5,
        title_font=dict(size=22, family="Arial Black"),
        xaxis_title=var,
        yaxis_title="Frecuencia",
        bargap=0.05,
        sliders=bins_slider,
        updatemenus=dropdown_menu,
        font=dict(size=13, family="Arial", color="black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
        legend_title_text="Género",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.6)")
    )

    return fig


# =========================================================
#                      UI
# =========================================================

app_ui = ui.page_fluid(
    ui.h2("Dashboard de Películas", style="text-align:center; font-weight:bold;"),

    ui.navset_tab(
        ui.nav_panel("Scatterplot", output_widget("plot_scatter")),
        ui.nav_panel("Mapa", output_widget("plot_mapa")),
        ui.nav_panel(
    "Frecuencias",
    ui.input_selectize(
        "var_hist",
        "Variable numérica:",
        choices=[c for c in df.columns if df[c].dtype in ["int64", "float64"]],
        selected="revenue"
    ),
    output_widget("plot_hist")
        )
    )
)


# =========================================================
#                      SERVER
# =========================================================

def server(input, output, session):

    @output
    @render_plotly
    def plot_scatter():
        return grafico_scatter()

    @output
    @render_plotly
    def plot_mapa():
        return grafico_mapa()

    @output
    @render_plotly
    def plot_hist():
        var = input.var_hist()
        return grafico_histogramas(var)


# =========================================================
#                      APP
# =========================================================

app = App(app_ui, server)