#Manipulacion de datos
import pandas as pd
import numpy as np

#Visualiciones (Plotly: scatter histogramas, mapa) 
import plotly.express as px
import plotly.graph_objects as go

#Para trabajar con archivos espaciales
import geopandas as gpd

#Para manejar datos en formato JSON
import json

from shinywidgets import output_widget, render_plotly
from shiny import App, render, ui, reactive

#Base principal con variables originales 
df = pd.read_excel("base_completa.xlsx")

#Se reemplazan NA y valores faltantes por None para evitar errores en Plotly
df = df.replace({pd.NA: None, np.nan: None})

#Base secundaria ajustada (para graficos descriptivos)
df2 = pd.read_excel("base_ajustada.xlsx")
df2 = df2.replace({pd.NA: None, np.nan: None})

# paleta

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


#Grafico de dispersion entre presupuesto y ganancia (Color -> género. Tamaño -> popularidad )
def grafico_scatter():
    #Lista de géneros sin repetir
    generos_unicos = df["genre_random"].dropna().unique()

    #Le da un color distinto a cada género
    color_map = {gen: custom_palette[i % len(custom_palette)] for i, gen in enumerate(generos_unicos)}

    #Grafico de dispersion principal
    fig = px.scatter(
        df,
        x="budget_mill",
        y="revenue_mill",
        color="genre_random",
        size="popularity",
        hover_data=["title", "language_adj"],
        opacity=0.9,
        color_discrete_map=color_map
    )

    #Los ajustes esteticos que se quisieron realizar
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_font=dict(size=14, color="black"),
        legend_font=dict(size=12, color="black"),
        font=dict(size=13, family="Arial", color="black"),
        xaxis=dict(showgrid=True, gridcolor="lightgray", tickfont=dict(size=13), title_font=dict(size=16)),
        yaxis=dict(showgrid=True, gridcolor="lightgray", tickfont=dict(size=13), title_font=dict(size=16))
    )
   
    return fig

#Mapa coroplético: muestra cuantas peliculas provienen de cada pais
def grafico_mapa():
    #Asegurar que la variable país sea string
    df["country_random"] = df["country_random"].astype(str)

    #Abrimos el mapa mundial
    mapa = gpd.read_file("naturalearth_countries/ne_110m_admin_0_countries.shp")

    #Realiza el conteo de peliculas por pais
    conteo = df.groupby("country_random").size().reset_index(name="conteo")

    #Unimos el mapa mundial con el conteo de peliculas por pais
    mapa_final = mapa.merge(conteo, left_on="ADMIN", right_on="country_random", how="left")

    #Reemplazamos NA por cero (países sin películas)
    mapa_final["conteo"] = mapa_final["conteo"].fillna(0)

    #Convertimos el mapa para que Plotly lo use
    geojson_data = json.loads(mapa_final.to_json())

    #Grafico coropléico
    fig = px.choropleth(
        mapa_final,
        geojson=geojson_data,
        locations=mapa_final.index,
        color="conteo",
        hover_name="ADMIN",
        color_continuous_scale="Sunset",
    )

    fig.update_geos(fitbounds="locations", visible=False)

    #Los ajustes esteticos que se quisieron realizar
    fig.update_coloraxes(
        cmin=0,
        cmax=100,
        colorbar=dict(
            ticks="outside",
            title=dict(
                    text="Cantidad de filmes",
                    font=dict(size=14, family="Arial", color="black")
            ),
            tickvals=list(range(0, 110, 10)),
            ticktext=[str(v) for v in range(0, 110, 10)]
        )
    )

    return fig


#Histogrmas: Muestra distribución de una variable seleccionada. Un histograma por genero. 
def grafico_histogramas(var):

    #Lista de generos
    generos = df["genre_random"].dropna().unique()

    #Se crea una figura con un histograma por genero
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

    #Control para cambiar cuántas barras se muestran
    steps = [dict(method="restyle", args=[{"nbinsx": b}], label=str(b)) for b in range(10, 110, 10)]

    bins_slider = [dict(active=2, steps=steps, currentvalue={"prefix": "Bins: "})]

    #Elige el género que se quiere ver
    buttons = []
    for i, gen in enumerate(generos):
        visibility = [False] * len(generos)
        visibility[i] = True
        buttons.append(dict(label=gen, method="update", args=[{"visible": visibility}]))

    dropdown_menu = [
        dict(buttons=buttons, direction="down", showactive=True, x=1.15, y=0.5)
    ]

    #Detalles del gráfico
    fig.update_layout(
        xaxis_title=var,
        yaxis_title="Frecuencia",
        bargap=0.05,
        updatemenus=dropdown_menu,
        sliders=bins_slider,
        font=dict(size=13, family="Arial", color="black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )

    fig.add_annotation(
    text="Género del filme:",  
    x=1.15, y=0.6,  
    xref="paper", yref="paper",
    showarrow=False,
    font=dict(size=14, family="Arial Black", color="black")
)


    return fig

#Graficos descriptivos
#Frecuencia de generos
def grafico_normal_1():
    conteo = df2["genre_random"].value_counts().reset_index()
    conteo.columns = ["genre_random", "count"]

    conteo = conteo.sort_values("count", ascending=True)

    fig = px.bar(
        conteo,
        x="count",
        y="genre_random",
        orientation="h",
        color_discrete_sequence=["#f55f74"],
        title=""
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_x=0.5,
        xaxis_title="Frecuencia",
        yaxis_title="Género"
    )

    return fig


#Frecuencia por continentes
def grafico_normal_2():
    conteo = df2["country_continent"].value_counts().reset_index()
    conteo.columns = ["country_continent", "count"]

    fig = px.bar(
        conteo,
        x="country_continent",
        y="count",
        color_discrete_sequence=["#0d7d87"],
        title=""
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_x=0.5,
        xaxis_title="Continente",
        yaxis_title="Frecuencia"
    )

    return fig


#Frecuencia de idiomas
def grafico_normal_3():
    conteo = df2["language_adj"].value_counts().reset_index()
    conteo.columns = ["language_adj", "count"]

    fig = px.treemap(
        conteo,
        path=["language_adj"],
        values="count",
        color="count",
        color_continuous_scale="Spectral",
        title=""
    )

    fig.update_traces(textfont_color="white")
    fig.update_layout(
        title_x=0.5,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


#Inferfaz de usuario
app_ui = ui.page_fluid(

    ui.tags.head(

        #Aplica un diseño visual a la app
        ui.tags.link(
            rel="stylesheet",
            href="https://bootswatch.com/5/lux/bootstrap.min.css"
        ),

        #Personaliza los colores del fondo, título y pestañas
        ui.tags.style(
            """
            body {
                background-color: #FFFFFF;
            }

            /* Color del título principal */
            .app-title {
                color: #000000;
            }

            /* Estilo base de las pestañas */
            .nav-tabs .nav-link {
                color: #000000 !important;
                font-weight: 600 !important;
            }

            /* Color al pasar el mouse sobre una pestaña */
            .nav-tabs .nav-link:hover {
                color: #a569bd !important;
            }

            /* Estilo de la pestaña activa */
            .nav-tabs .nav-link.active {
                background-color: #d7bde2 !important;
                color: white !important;
                border-radius: 8px !important;
                border-color: #d7bde2 !important;
            }
            """
        )
    ),

    #Título principal de la aplicación
    ui.h2(
        "Análisis descriptivo: Películas",
        style="text-align:center",
        class_="app-title"
    ),

    #Conjunto de pestañas de navegación principales de la aplicación
    ui.navset_tab(

        #Pestaña 1: Gráficos descriptivos
        ui.nav_panel(
            "Gráficos descriptivos",

            #Grafico 1
            ui.h4("Gráfico 1. Frecuencia del género de las películas", style="text-align:center"),
            output_widget("plot_normal_1"),
            ui.br(),

            #Grafico 2
            ui.h4("Gráfico 2. Frecuencia por continente", style="text-align:center"),
            output_widget("plot_normal_2"),
            ui.br(),

            #Grafico 3
            ui.h4("Gráfico 3. Frecuencia de idiomas originales de los filmes", style="text-align:center"),
            output_widget("plot_normal_3")
        ),

        #Pestaña 2: Scatterplot
        ui.nav_panel(
            "Scatterplot",
            ui.h4("Presupuesto y ganancia: género y popularidad", style="text-align:center"),
            output_widget("plot_scatter")
        ),

        #Pestaña 3: Mapa
        ui.nav_panel(
            "Mapa",
            ui.h4("Cantidad de películas por país", style="text-align:center"),
            output_widget("plot_mapa")
        ),

        #Pestaña 4: Histogramas dinámicos
        ui.nav_panel(
            "Frecuencias",

            # Título reactivo generado desde el server
            ui.output_ui("titulo_hist"),

            # Selector para elegir qué variable numérica graficar
            ui.input_selectize(
                "var_hist",
                "Variable numérica:",
                choices=[c for c in df.columns if df[c].dtype in ("int64", "float64")],
                selected="revenue"
            ),

            # Gráfico de histograma dinámico
            output_widget("plot_hist")
        )
    )
)


def server(input, output, session):

    #Muestra el scatterplot dentro de output_widget("plot_scatter")
    @output
    @render_plotly
    def plot_scatter():
        return grafico_scatter()

    #Muestra el mapa dentro de output_widget("plot_mapa")
    @output
    @render_plotly
    def plot_mapa():
        return grafico_mapa()

    #Título dinámico del histograma, se actualiza según la variable seleccionada
    @output
    @render.ui
    def titulo_hist():
        var = input.var_hist()
        return ui.h4(f"Distribución de {var} por género del filme", style="text-align:center")

    #Gráficos descriptivos (1, 2 y 3)
    @output
    @render_plotly
    def plot_normal_1():
        return grafico_normal_1()

    @output
    @render_plotly
    def plot_normal_2():
        return grafico_normal_2()

    @output
    @render_plotly
    def plot_normal_3():
        return grafico_normal_3()

    #Muestra el histograma dinámico según la variable elegida
    @output
    @render_plotly
    def plot_hist():
        return grafico_histogramas(input.var_hist())

# Se construye la app 
app = App(app_ui, server)
