from __future__ import annotations

from pathlib import Path

from dash import Dash, Input, Output, dcc, html, State, dash_table
import pandas as pd
from flask_caching import Cache

from .analysis import build_kpis, by_accident_type, by_period, by_state, monthly_trend, weekend_comparison
from .data import load_raw_accidents, generate_demo_data
from .figures import accident_type_bar, kpi_figure, monthly_line, period_donut, scatter_severity, state_bar, weekend_bars

PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    data = load_raw_accidents()
except Exception as exc:
    # if loading real CSVs is slow or fails, fall back to demo dataset so the app starts
    print("Warning: load_raw_accidents failed, falling back to demo data:", exc)
    data = generate_demo_data(rows=20000)

app = Dash(__name__, title="Acidentes de Trânsito PRF", assets_folder=str(PROJECT_ROOT / "assets"))
cache = Cache(app.server, config={"CACHE_TYPE": "SimpleCache"})

DISPLAY_COLUMNS = [
    "occurred_at",
    "state",
    "city",
    "br",
    "km",
    "accident_type",
    "classificacao_acidente",
    "fatalities",
    "injured",
    "vehicles",
    "severity",
    "source_file",
]

COLUMN_LABELS = {
    "occurred_at": "Data e hora",
    "state": "UF",
    "city": "Município",
    "br": "BR",
    "km": "Km",
    "accident_type": "Causa",
    "classificacao_acidente": "Classificação",
    "fatalities": "Mortos",
    "injured": "Feridos",
    "vehicles": "Veículos",
    "severity": "Severidade",
    "source_file": "Arquivo",
}


def _card(title: str, component_id: str) -> html.Div:
    return html.Div(
        [
            html.H4(title, className="card-title"),
            dcc.Graph(id=component_id, config={"displayModeBar": False}),
        ],
        className="card",
    )


def _safe_range(column: str, default: tuple[float, float] = (0.0, 1000.0)) -> tuple[float, float]:
    if column not in data.columns:
        return default
    values = pd.to_numeric(data[column], errors="coerce").dropna()
    if values.empty:
        return default
    return float(values.min()), float(values.max())


def _format_number(value: float | int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _filter_data(state, start_date, end_date, severity, city, km_range) -> pd.DataFrame:
    filtered = data.copy()
    if state:
        filtered = filtered[filtered["state"].isin(state if isinstance(state, list) else [state])]
    if start_date:
        filtered = filtered[filtered["occurred_at"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["occurred_at"] <= pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)]
    if severity:
        filtered = filtered[filtered["severity"].isin(severity if isinstance(severity, list) else [severity])]
    if city:
        filtered = filtered[filtered["city"].isin(city if isinstance(city, list) else [city])]
    if km_range and "km" in filtered.columns:
        try:
            low, high = (float(km_range[0]), float(km_range[1])) if isinstance(km_range, (list, tuple)) else (float(km_range), float(km_range))
            filtered = filtered[(filtered["km"] >= low) & (filtered["km"] <= high)]
        except Exception:
            pass
    return filtered


km_min, km_max = _safe_range("km")


app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Dashboard de Acidentes de Trânsito"),
                html.P("Dados PRF/Datatran com visão executiva, filtros e tabela navegável."),
            ],
            className="hero",
        ),
                dcc.Tabs(
                    id="tabs",
                    value="overview",
                    className="tabs",
                    children=[
                        dcc.Tab(label="Visão geral", value="overview", className="tab", selected_className="tab--selected", children=[
                    html.Div(
                        [
                            html.Div(className="kpi-grid", children=[
                                html.Div(id="kpi-total", className="kpi-card"),
                                html.Div(id="kpi-fatalities", className="kpi-card"),
                                html.Div(id="kpi-injured", className="kpi-card"),
                                html.Div(id="kpi-severe", className="kpi-card"),
                            ]),
                            html.Div(className="grid-two", children=[
                                _card("Tendência mensal", "chart-monthly"),
                                _card("UFs com mais acidentes", "chart-state"),
                            ]),
                            html.Div(className="grid-two", children=[
                                _card("Principais causas", "chart-type"),
                                _card("Períodos do dia", "chart-period"),
                            ]),
                            html.Div(className="grid-two", children=[
                                    html.Div(children=[
                                        html.Div(className="card", children=[
                                            html.Div([html.Button("Carregar mapa", id="btn-load-map", n_clicks=0, className="primary-button")], style={"textAlign": "right", "marginBottom": "8px"}),
                                            dcc.Graph(id="chart-map", config={"displayModeBar": False}),
                                        ])
                                    ]),
                                    _card("Mapa de calor horário", "chart-heatmap"),
                            ]),
                        ],
                        className="page",
                    )
                ]),
                dcc.Tab(label="Exploração", value="explore", className="tab", selected_className="tab--selected", children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label("Data"),
                                            dcc.DatePickerRange(
                                                id="date-range",
                                                start_date=data["occurred_at"].min().date() if not data.empty else None,
                                                end_date=data["occurred_at"].max().date() if not data.empty else None,
                                            ),
                                        ],
                                        className="filter",
                                    ),
                                    html.Div(
                                        [
                                            html.Label("UF"),
                                            dcc.Dropdown(
                                                id="state-filter",
                                                options=[{"label": s, "value": s} for s in sorted(data["state"].dropna().unique())],
                                                value=None,
                                                multi=True,
                                            ),
                                        ],
                                        className="filter",
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Município"),
                                            dcc.Dropdown(
                                                id="city-filter",
                                                options=[{"label": c, "value": c} for c in sorted(data.get("city", pd.Series(dtype=str)).dropna().unique())],
                                                value=None,
                                                multi=True,
                                            ),
                                        ],
                                        className="filter",
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Severidade"),
                                            dcc.Dropdown(
                                                id="severity-filter",
                                                options=[{"label": s.title(), "value": s} for s in sorted(data["severity"].dropna().unique())],
                                                value=None,
                                                multi=True,
                                            ),
                                        ],
                                        className="filter",
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Quilometragem (km)"),
                                            dcc.RangeSlider(
                                                id="km-range",
                                                min=km_min,
                                                max=km_max,
                                                value=[km_min, km_max],
                                                marks={
                                                    int(km_min): f"{int(km_min):,}".replace(",", "."),
                                                    int(km_max): f"{int(km_max):,}".replace(",", "."),
                                                },
                                                tooltip={"placement": "bottom", "always_visible": False},
                                                step=1,
                                            ),
                                        ],
                                        className="filter",
                                    ),
                                    html.Div(className="filter", children=[
                                        html.Button("Exportar CSV filtrado", id="btn-download", className="primary-button"),
                                        dcc.Download(id="download-data"),
                                    ]),
                                ],
                                className="filters",
                            ),
                            html.Div(id="filter-summary", className="summary-grid"),
                            html.Div(className="grid-two", children=[
                                _card("Comparação por causa", "chart-explore-type"),
                                _card("Comparação temporal", "chart-explore-line"),
                            ]),
                            html.Div(className="grid-two", children=[
                                _card("Distribuição por período", "chart-explore-period"),
                                _card("Fim de semana vs úteis", "chart-explore-weekend"),
                            ]),
                            html.Div(className="card", children=[
                                html.H4("Relação entre variáveis"),
                                dcc.Graph(id="chart-scatter", config={"displayModeBar": False}),
                            ]),
                            html.Div(className="card", children=[
                                html.H4("Tabela de registros"),
                                dash_table.DataTable(
                                    id="table-explore",
                                        columns=[],
                                        data=[],
                                        page_size=15,
                                        page_current=0,
                                        page_action='custom',
                                        sort_action='custom',
                                        sort_mode='single',
                                        sort_by=[],
                                    style_table={"overflowX": "auto"},
                                    style_cell={"textAlign": "left", "padding": "8px", "fontSize": "13px", "whiteSpace": "normal"},
                                    style_header={"fontWeight": "700", "backgroundColor": "#eef2f7"},
                                    style_data_conditional=[
                                        {"if": {"row_index": "odd"}, "backgroundColor": "#f8fafc"}
                                    ],
                                ),
                            ]),
                        ],
                        className="page",
                    )
                ]),
            ],
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("kpi-total", "children"),
    Output("kpi-fatalities", "children"),
    Output("kpi-injured", "children"),
    Output("kpi-severe", "children"),
    Output("chart-monthly", "figure"),
    Output("chart-state", "figure"),
    Output("chart-type", "figure"),
    Output("chart-period", "figure"),
    Output("chart-heatmap", "figure"),
    Input("tabs", "value"),
)
def update_overview(_: str):
    kpis = build_kpis(data)
    monthly = monthly_trend(data)
    states = by_state(data)
    accident_types = by_accident_type(data)
    periods = by_period(data)
    # cached geo
    # defer heavy map generation — render empty placeholder here
    map_fig = {}
    heat_fig = None
    try:
        from .figures import hourly_heatmap
        heat_fig = hourly_heatmap(data)
    except Exception:
        heat_fig = {}
    # build lightweight KPI HTML children
    def _kpi_html(value, label, suffix=""):
        display = f"{value:.0f}{suffix}" if suffix == "%" else (f"{int(value):,}" if isinstance(value, (int, float)) else str(value))
        display = display.replace(",", ".")
        return html.Div([html.Div(display, className="num"), html.Div(label, className="lbl")])

    return (
        _kpi_html(kpis["total_accidents"], "Acidentes totais"),
        _kpi_html(kpis["fatalities"], "Fatalidades"),
        _kpi_html(kpis["injured"], "Feridos"),
        _kpi_html(kpis["severe_share"] * 100, "Participação de casos graves", suffix="%"),
        monthly_line(monthly),
        state_bar(states),
        accident_type_bar(accident_types),
        period_donut(periods),
        heat_fig,
    )


@app.callback(
    Output("chart-explore-type", "figure"),
    Output("chart-explore-line", "figure"),
    Output("chart-explore-period", "figure"),
    Output("chart-explore-weekend", "figure"),
    Output("chart-scatter", "figure"),
    Input("state-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("severity-filter", "value"),
    Input("city-filter", "value"),
    Input("km-range", "value"),
)
def update_explore(state, start_date, end_date, severity, city, km_range):
    filtered = _filter_data(state, start_date, end_date, severity, city, km_range)

    type_data = by_accident_type(filtered)
    monthly = monthly_trend(filtered)
    period_data = by_period(filtered)
    weekend_data = weekend_comparison(filtered)

    scatter_source = filtered

    from .figures import accident_type_bar, monthly_line, period_donut, weekend_bars, scatter_severity

    return (
        accident_type_bar(type_data),
        monthly_line(monthly),
        period_donut(period_data),
        weekend_bars(weekend_data),
        scatter_severity(scatter_source, "injured", "fatalities"),
    )



@app.callback(
    Output("table-explore", "data"),
    Output("table-explore", "columns"),
    Output("table-explore", "page_count"),
    Output("filter-summary", "children"),
    Input("state-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("severity-filter", "value"),
    Input("city-filter", "value"),
    Input("km-range", "value"),
    Input("table-explore", "page_current"),
    Input("table-explore", "page_size"),
    Input("table-explore", "sort_by"),
)
def update_table(state, start_date, end_date, severity, city, km_range, page_current, page_size, sort_by):
    df = _filter_data(state, start_date, end_date, severity, city, km_range)

    # sorting
    if sort_by:
        col = sort_by[0]["column_id"]
        asc = sort_by[0]["direction"] == "asc"
        if col in df.columns:
            df = df.sort_values(col, ascending=asc)

    # select columns to show
    available = [c for c in DISPLAY_COLUMNS if c in df.columns]
    tbl = df[available].copy()
    if "occurred_at" in tbl.columns:
        tbl["occurred_at"] = tbl["occurred_at"].dt.strftime("%d/%m/%Y %H:%M")

    # pagination slice
    start = page_current * page_size
    end = start + page_size
    page_df = tbl.iloc[start:end].copy()

    # format numeric columns vectorized
    for numc in ("fatalities", "injured", "vehicles", "br"):
        if numc in page_df.columns:
            page_df[numc] = pd.to_numeric(page_df[numc], errors="coerce").fillna(0).astype(int).map(lambda value: f"{value:,}".replace(",", "."))
    if "km" in page_df.columns:
        page_df["km"] = pd.to_numeric(page_df["km"], errors="coerce").map(lambda value: "" if pd.isna(value) else f"{value:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))

    data_records = page_df.to_dict("records")
    columns = [{"name": COLUMN_LABELS.get(col, col.replace("_", " ").title()), "id": col} for col in available]
    page_count = max(1, (len(tbl) + page_size - 1) // page_size)
    summary = [
        html.Div([html.Div(_format_number(len(df)), className="summary-value"), html.Div("registros filtrados", className="summary-label")], className="summary-card"),
        html.Div([html.Div(_format_number(df["fatalities"].fillna(0).sum()), className="summary-value"), html.Div("mortos", className="summary-label")], className="summary-card"),
        html.Div([html.Div(_format_number(df["injured"].fillna(0).sum()), className="summary-value"), html.Div("feridos", className="summary-label")], className="summary-card"),
        html.Div([html.Div(_format_number(df["state"].nunique()), className="summary-value"), html.Div("UFs no filtro", className="summary-label")], className="summary-card"),
    ]
    return data_records, columns, page_count, summary


@app.callback(
    Output("chart-map", "figure"),
    Input("btn-load-map", "n_clicks"),
)
def load_map(n_clicks):
    # only generate the map when user requests it
    if not n_clicks:
        return {}
    try:
        from .figures import collisions_map
        fig = collisions_map(data)
        return fig
    except Exception:
        return {}


@app.callback(
    Output("download-data", "data"),
    Input("btn-download", "n_clicks"),
    State("state-filter", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    State("severity-filter", "value"),
    State("city-filter", "value"),
    State("km-range", "value"),
    prevent_initial_call=True,
)
def download_filtered(_, state, start_date, end_date, severity, city, km_range):
    filtered = _filter_data(state, start_date, end_date, severity, city, km_range)
    available = [column for column in DISPLAY_COLUMNS if column in filtered.columns]
    export = filtered[available].copy()
    if "occurred_at" in export.columns:
        export["occurred_at"] = export["occurred_at"].dt.strftime("%d/%m/%Y %H:%M")
    return dcc.send_data_frame(export.to_csv, "acidentes_filtrados.csv", index=False)
