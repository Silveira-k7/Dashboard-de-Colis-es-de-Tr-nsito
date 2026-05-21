from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


COLOR_SCALE = ["#1f4e79", "#2e7d8a", "#f29f05", "#d1495b"]


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#64748b"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(template="plotly_white", height=340, margin=dict(l=20, r=20, t=20, b=20))
    return fig


def kpi_figure(value: float, label: str, suffix: str = "") -> go.Figure:
    def _compact(n: float) -> str:
        try:
            n = float(n)
        except Exception:
            return str(n)
        if abs(n) >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if abs(n) >= 1_000:
            return f"{n/1_000:.1f}K"
        return f"{int(n):,}"

    display = f"{value:.0f}{suffix}" if suffix == "%" else _compact(value)

    fig = go.Figure()
    fig.add_annotation(
        text=f"<b>{display}</b><br><span style='font-size:14px'>{label}</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=26, color="#0f1724"),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", plot_bgcolor="white")
    return fig


def monthly_line(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return _empty_figure("Sem registros para o filtro selecionado")
    # ensure month_period is datetime
    if "month_period" in frame.columns and pd.api.types.is_datetime64_any_dtype(frame["month_period"]):
        mp = frame.copy()
        month_map = {1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun", 7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"}
        mp = mp.assign(month_label=mp["month_period"].dt.month.map(month_map) + " " + mp["month_period"].dt.year.astype(str))
        fig = px.line(mp, x="month_period", y="accidents", markers=True, title="Evolução mensal dos acidentes")
        fig.update_traces(line=dict(color=COLOR_SCALE[0], width=3), hovertemplate="%{x|%b %Y}: %{y:,} acidentes")
        fig.update_layout(template="plotly_white", height=360, xaxis_title="Mês", yaxis_title="Acidentes")
        fig.update_xaxes(tickvals=mp["month_period"].tolist(), ticktext=mp["month_label"].tolist())
    else:
        fig = px.line(frame, x="month_period", y="accidents", markers=True, title="Evolução mensal dos acidentes")
        fig.update_traces(line=dict(color=COLOR_SCALE[0], width=3), hovertemplate="%{x}: %{y:,} acidentes")
        fig.update_layout(template="plotly_white", height=360, xaxis_title="Mês", yaxis_title="Acidentes")
    return fig


def state_bar(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return _empty_figure("Sem UFs para exibir")
    top = frame.head(10).copy()
    top["label"] = top["accidents"].map(lambda value: f"{int(value):,}".replace(",", "."))
    fig = px.bar(top, x="accidents", y="state", orientation="h", title="Top 10 UFs por acidentes")
    fig.update_traces(marker_color=COLOR_SCALE[1], text=top["label"], textposition="outside", cliponaxis=False)
    fig.update_layout(template="plotly_white", height=420, xaxis_title="Acidentes", yaxis_title="Estado", margin=dict(l=70, r=90, t=70, b=50))
    fig.update_xaxes(range=[0, max(top["accidents"].max() * 1.18, 1)])
    fig.update_yaxes(autorange="reversed")
    return fig


def accident_type_bar(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return _empty_figure("Sem causas para exibir")
    top = frame.head(15).copy()
    top["label"] = top["accidents"].map(lambda value: f"{int(value):,}".replace(",", "."))
    fig = px.bar(top, x="accidents", y="accident_type", orientation="h", title="Principais causas de acidentes")
    fig.update_traces(marker_color=COLOR_SCALE[2], text=top["label"], textposition="outside", cliponaxis=False, hovertemplate="%{x:,} acidentes<br>%{y}")
    fig.update_layout(template="plotly_white", height=460, xaxis_title="Acidentes", yaxis_title="Causa", margin=dict(l=220, r=90, t=70, b=50))
    fig.update_xaxes(range=[0, max(top["accidents"].max() * 1.18, 1)])
    fig.update_yaxes(autorange="reversed")
    return fig


def period_donut(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return _empty_figure("Sem períodos para exibir")
    fig = px.pie(frame, names="time_period", values="accidents", title="Distribuição por período do dia", hole=0.45)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(template="plotly_white", height=360)
    return fig


def collisions_map(frame: pd.DataFrame) -> go.Figure:
    if {"latitude", "longitude"}.issubset(frame.columns):
        sample = frame.dropna(subset=["latitude", "longitude"]).head(2000)
        # prepare customdata for formatted hovertemplate
        sample = sample.assign(_occurred=sample["occurred_at"].dt.strftime("%Y-%m-%d %H:%M"), _injured=sample.get("injured", 0), _fatal=sample.get("fatalities", 0))
        fig = px.scatter_mapbox(
            sample,
            lat="latitude",
            lon="longitude",
            color="severity",
            hover_name="city" if "city" in sample.columns else None,
            custom_data=["_occurred", "_injured", "_fatal", "accident_type"],
            zoom=4,
            height=420,
            title="Mapa de acidentes (amostra)",
            color_discrete_sequence=COLOR_SCALE,
            mapbox_style="open-street-map",
        )
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Data: %{customdata[0]}<br>Feridos: %{customdata[1]:,}<br>Mortos: %{customdata[2]:,}<br>Causa: %{customdata[3]}"
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        return fig
    return _empty_figure("Latitude e longitude não estão disponíveis")


def hourly_heatmap(frame: pd.DataFrame) -> go.Figure:
    if "occurred_at" in frame.columns:
        # translate day names to pt-BR
        day_map = {
            "Monday": "Segunda",
            "Tuesday": "Terça",
            "Wednesday": "Quarta",
            "Thursday": "Quinta",
            "Friday": "Sexta",
            "Saturday": "Sábado",
            "Sunday": "Domingo",
        }
        tmp = frame.dropna(subset=["occurred_at"]).assign(hour=lambda d: d["occurred_at"].dt.hour, day=lambda d: d["occurred_at"].dt.day_name().map(day_map))
        pivot = (
            tmp.groupby(["day", "hour"]).size().reset_index(name="count").pivot(index="day", columns="hour", values="count").fillna(0)
        )
        # Ensure weekday order
        days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        available = [d for d in days if d in pivot.index]
        z = pivot.loc[available].values if not pivot.empty else [[]]
        fig = go.Figure(data=go.Heatmap(z=z, x=pivot.columns.tolist() if not pivot.empty else [], y=available, colorscale="Viridis", hovertemplate="%{y} %{x}h: %{z} acidentes"))
        fig.update_layout(title="Mapa de calor por hora e dia", xaxis_title="Hora do dia", yaxis_title="Dia da semana", height=420)
        return fig
    return _empty_figure("Sem datas para montar o mapa de calor")


def weekend_bars(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return _empty_figure("Sem registros para comparar")
    fig = px.bar(frame, x="day_type", y="accidents", title="Dias úteis vs fim de semana", text="accidents")
    fig.update_traces(marker_color=COLOR_SCALE[3], textposition="outside")
    fig.update_layout(template="plotly_white", height=340, xaxis_title="Tipo de dia", yaxis_title="Acidentes")
    return fig


def scatter_severity(frame: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
    if frame.empty:
        return _empty_figure("Sem registros para o filtro selecionado")
    fig = px.scatter(
        frame,
        x=x_col,
        y=y_col,
        color="severity",
        hover_data=["state", "city", "accident_type", "occurred_at"],
        title="Relação entre feridos e mortos",
        color_discrete_sequence=COLOR_SCALE,
    )
    fig.update_traces(hovertemplate="%{x:,} %{xaxis.title.text}<br>%{y:,} %{yaxis.title.text}<br>%{customdata[0]} - %{customdata[1]}<br>%{customdata[2]}")
    fig.update_layout(template="plotly_white", height=360)
    return fig
