"""Stage 4: Dash dashboard — visualise which domains apps contact, and how often.

Reads the current state of the database (produced by capture → enrich → classify)
and presents it interactively. Static read with a manual refresh button; not
auto-updating live (see README limitations).
"""

import sqlite3

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output

import config


def load_data():
    """Read one aggregated row per domain from the database."""
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT domain,
               COUNT(*)              AS contacts,
               MAX(category)         AS category,
               MAX(score)            AS anomaly
        FROM domains
        GROUP BY domain
        ORDER BY contacts DESC
        """,
        conn,
    )
    conn.close()
    return df


app = Dash(__name__)
app.title = "Consent Radar"


def build_layout():
    df = load_data()
    total_domains = len(df)
    total_trackers = int((df["category"] == "tracker").sum())
    total_contacts = int(df["contacts"].sum())

    return html.Div(
        style={"fontFamily": "sans-serif", "maxWidth": "1000px",
               "margin": "0 auto", "padding": "20px"},
        children=[
            html.H1("Consent Radar"),
            html.P("Which domains are your apps quietly talking to?"),

            html.Div(
                style={"display": "flex", "gap": "30px", "margin": "20px 0"},
                children=[
                    html.Div([html.H2(str(total_domains)),
                              html.P("distinct domains")]),
                    html.Div([html.H2(str(total_trackers)),
                              html.P("flagged trackers")]),
                    html.Div([html.H2(str(total_contacts)),
                              html.P("total contacts")]),
                ],
            ),

            html.Button("Refresh", id="refresh", n_clicks=0,
                        style={"marginBottom": "20px"}),

            dcc.Graph(id="bar"),

            html.H3("All domains (sortable)"),
            dash_table.DataTable(
                id="table",
                columns=[
                    {"name": "Domain", "id": "domain"},
                    {"name": "Contacts", "id": "contacts"},
                    {"name": "Category", "id": "category"},
                    {"name": "Anomaly", "id": "anomaly",
                     "type": "numeric",
                     "format": {"specifier": ".3f"}},
                ],
                sort_action="native",
                page_size=15,
                style_cell={"textAlign": "left", "padding": "6px"},
                style_data_conditional=[
                    {"if": {"filter_query": '{category} = "tracker"'},
                     "backgroundColor": "#ffe5e5"},
                ],
            ),
        ],
    )


app.layout = build_layout


@app.callback(
    Output("bar", "figure"),
    Output("table", "data"),
    Input("refresh", "n_clicks"),
)
def refresh(_n_clicks):
    df = load_data()
    top = df.head(15)
    fig = px.bar(
        top, x="contacts", y="domain", orientation="h",
        color="category",
        color_discrete_map={"tracker": "#d62728", "other": "#7f7f7f"},
        title="Top 15 domains by contact count",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig, df.to_dict("records")


if __name__ == "__main__":
    app.run(debug=True)