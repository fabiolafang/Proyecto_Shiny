import pandas as pd
import plotly.express as px
from shiny import App, render, ui, reactive
from shinywidgets import render_plotly


#      CARGA DE DATOS

df = pd.read_excel("filmes.xlsx")

cols_num = ["budget","revenue","vote_average","popularity","vote_count","runtime"]
df[cols_num] = df[cols_num].apply(pd.to_numeric, errors="coerce")


#            UI

app_ui = ui.page_fluid(
    ui.h2("Análisis interactivo de películas"),

    ui.layout_sidebar(
        ui.sidebar(

            ui.input_select(
                "xvar", "Variable numérica:",
                ["budget", "revenue", "vote_average", "popularity", "vote_count", "runtime"]
            ),

            ui.input_select(
                "catvar", "Variable categórica:",
                ["genre_random", "language_adj", "country_continent"]
            ),

            ui.input_slider("bins", "Número de bins (histograma):", 5, 100, 30),

            ui.input_checkbox("log", "Escala logarítmica", False)
        ),

        ui.div(
            ui.h3("Histograma"),
            ui.output_plot("hist"),

            ui.h3("Boxplot por categoría"),
            ui.output_plot("box"),

            ui.h3("Frecuencias categóricas"),
            ui.output_plot("bars"),

            ui.h3("Relación Budget vs Revenue"),
            ui.output_plot("scatter")
        )
    )
)


#          SERVER

def server(input, output, session):

    @reactive.Calc
    def datos():
        return df.copy()


    # HISTOGRAMA

    @output
    @render_plotly
    def hist():
        d = datos()

        fig = px.histogram(
            d,
            x=input.xvar(),
            nbins=input.bins(),
            title=f"Distribución de {input.xvar()}",
            opacity=0.75
        )

        if input.log():
            fig.update_xaxes(type="log")

        return fig

 
    # BOXPLOT

    @output
    @render_plotly
    def box():
        d = datos()

        fig = px.box(
            d,
            x=input.catvar(),
            y=input.xvar(),
            title=f"{input.xvar()} por {input.catvar()}",
            points="all"
        )

        if input.log():
            fig.update_yaxes(type="log")

        return fig


    # BARRAS (FRECUENCIAS)

    @output
    @render_plotly
    def bars():
        d = datos()

        counts = d[input.catvar()].value_counts().reset_index()
        counts.columns = ["categoria", "frecuencia"]

        fig = px.bar(
            counts,
            x="categoria",
            y="frecuencia",
            title=f"Frecuencia de {input.catvar()}"
        )

        return fig


    # SCATTER BUDGET VS REVENUE

    @output
    @render_plotly
    def scatter():
        d = datos()

        fig = px.scatter(
            d,
            x="budget",
            y="revenue",
            color="genre_random",
            hover_data=["title", "popularity"],
            title="Relación Budget vs Revenue"
        )

        if input.log():
            fig.update_xaxes(type="log")
            fig.update_yaxes(type="log")

        return fig


app = App(app_ui, server)
