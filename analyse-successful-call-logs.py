import re
import pandas as pd
import datetime
import plotly.express as px


def normalise_duration_to_hours(duration_text):
    """
    Normalises duration in various string formats to hours as a float

    e.g: 'a minute' to 0.01666...
    e.g: 'an hour' to 1
    e.g: '60 minutes' to 1
    e.g: '1 hour' to 1
    """

    # Parse magnitude
    # Match 'a' or 'an' or a number
    regex = r"(\ban\b|\ba\b|\b\d+\b)"

    match = re.search(regex, duration_text)

    if match:
        if match.group() in ["a", "an"]:
            magnitude = 1
        else:
            magnitude = float(match.group())
    else:
        magnitude = 0

    # Handle unit
    if "hour" in duration_text:
        return magnitude
    elif "minute" in duration_text:
        return magnitude / 60
    else:
        return None


def parse_raw_text(raw_text):
    """
    Parses the constituent parts out of the raw text

    Caller, Duration (hours), Date Time
    e.g: Gorilliath started a call that lasted 2 hours. — 03/04/2024 23:06
    e.g: Gorilliath started a call. — 03/04/2024 23:06
    """
    caller_maybe_duration_part, date_time_part = raw_text.split(" — ")

    # Caller and Duration
    if "that lasted" in caller_maybe_duration_part:
        caller, duration_part = caller_maybe_duration_part.split(
            " started a call that lasted "
        )
        duration = normalise_duration_to_hours(duration_part)
    else:
        caller = caller_maybe_duration_part.split(" started a call.")[0]
        duration = 0

    # Date Time
    date_time = datetime.datetime.strptime(date_time_part, "%d/%m/%Y %H:%M")

    return pd.Series([caller, duration, date_time])


def plot_scatter(df):
    fig = px.scatter(
        df,
        x="Date Time",
        y="Duration (hours)",
        color="Caller",
        hover_data=["ID"],
        title="Duration of successful calls",
    )
    fig.update_xaxes(title_text="Date Time")
    fig.update_yaxes(title_text="Duration (hours)")

    fig.update_traces(marker_size=7)

    # Date Time slicing
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            )
        ),
        xaxis_rangeslider_visible=True,
    )

    fig.write_html(f"./output/scatter-duration-of-successful-calls.html")


def plot_histogram(df):
    df["Year"] = pd.to_datetime(df["Date Time"]).dt.year

    fig = px.histogram(
        df,
        x="Date Time",
        y="Duration (hours)",
        color="Year",
        title="Total duration of successful calls each month",
    )
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Duration (hours)")

    # Histogram bins should be for each month
    fig.update_traces(xbins_size="M1")

    fig.write_html(
        f"./output/histogram-total-duration-of-successful-calls-each-month.html"
    )


if __name__ == "__main__":
    # Load the raw data
    df = pd.read_csv("./output/successful-call-logs.csv")

    # Parse 'Raw Text' to its constituent parts and extend the dataframe with it
    df[["Caller", "Duration (hours)", "Date Time"]] = df["Raw Text"].apply(
        parse_raw_text
    )

    # Write to a new CSV file
    df.to_csv("./output/analysed-successful-call-logs.csv", index=False)

    plot_scatter(df)
    plot_histogram(df)
