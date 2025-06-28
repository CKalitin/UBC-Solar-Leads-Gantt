import plotly.graph_objects as go
import pandas as pd

def parse_file():
    """
    Data Format:
    Role
    Name, start date, end date

    Eg.
    Team Captain
    Alex Ezzat, 1969-07-20, 2025-07-04
    """
    data = []
    current_team = None

    with open("lead_data.txt") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tokens = line.split()
            if len(tokens) >= 3 and tokens[-2].count("-") == 2 and tokens[-1].count("-") == 2:
                # Likely a data line
                start, end = tokens[-2], tokens[-1]
                name = " ".join(tokens[:-2])
                data.append({
                    "Team": current_team,
                    "Lead": name,
                    "Start": start,
                    "End": end
                })
            else:
                # New team header
                current_team = line
    print(data)
    return data

data = parse_file()

df = pd.DataFrame(data)
df["Start"] = pd.to_datetime(df["Start"])
df["End"] = pd.to_datetime(df["End"])
df["Duration"] = (df["End"] - df["Start"]).dt.days

fig = go.Figure()

teams = df["Team"].unique()
color_map = {team: f"hsl({i*360/len(teams)},50%,50%)" for i, team in enumerate(teams)}

for _, row in df.iterrows():
    fig.add_trace(go.Bar(
        x=[row["Duration"]],
        y=[row["Team"]],
        base=row["Start"],
        orientation='h',
        marker_color=color_map[row["Team"]],
        text=row["Lead"],
        textposition="inside",
        hovertemplate=f"Lead: {row['Lead']}<br>Start: {row['Start'].date()}<br>End: {row['End'].date()}<extra></extra>"
    ))

fig.update_layout(
    title="Team Lead Timeline",
    barmode="stack",
    xaxis_title="Date",
    yaxis_title="Team",
    yaxis_autorange="reversed",
    bargap=0.2,
)

fig.show()
