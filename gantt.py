import plotly.express as px
import pandas as pd

team_color_map = {
    "Team Captain": "#FF5733",
    "Elec Lead": "#3336FF",
    "Mech Lead": "#00A835",
    "Battery Management System": "#FF8C00",
    "Battery Mechanical": "#FF8C00",
}

team_order = [
    "Team Captain",
    "Elec Lead",
    "Mech Lead",
    "Battery Management System",
    "Battery Mechanical",
    "Marketing",
    "Business",
    "LV Systems",
    "Power Electronics",
    "Power and Signals",
    "Software",
    "Embedded",
    "Race Strategy",
    "Chassis",
    "Structures",
    "Aeroshell",
    "Aerodynamics",
    "Suspension, Steering, Wheels, and Breaking",
    "Vehicle Dynamics",
]

# Need color map per person because Plotly
display_color_map = {}

def parse_file():
    data = []
    current_team = None
    with open("lead_data.txt") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tokens = line.split()
            if len(tokens) >= 3 and tokens[-2].count("-") == 2 and tokens[-1].count("-") == 2:
                start, end = tokens[-2], tokens[-1]
                name = " ".join(tokens[:-2]).replace(",", "")
                data.append({
                    "Team": current_team,
                    "Lead": name,
                    "Start": start,
                    "End": end
                })
                display_color_map[name] = team_color_map.get(current_team, "#000000")  # Default to black if not found
            else:
                current_team = line
    return data

data = parse_file()

df = pd.DataFrame(data)
df["Start"] = pd.to_datetime(df["Start"].str.replace(",", ""))
df["End"] = pd.to_datetime(df["End"].str.replace(",", ""))
df["Offset"] = 0
offset_tracker = {}  # Dict of {team: list of (end_time, offset)}

for idx, row in df.iterrows():
    team = row["Team"]
    start = row["Start"]
    end = row["End"]
    
    if team not in offset_tracker:
        offset_tracker[team] = []

    taken_offsets = set()

    # Find which offsets are occupied at this bar's start time
    for prev_end, offset in offset_tracker[team]:
        if prev_end > start:
            taken_offsets.add(offset)
    
    # Assign lowest available offset
    offset = 0
    while offset in taken_offsets:
        offset += 1

    df.loc[idx, "Offset"] = offset
    offset_tracker[team].append((end, offset))

df["Y"] = df["Team"] + " (" + df["Offset"].astype(str) + ")"
df["ColorGroup"] = df["Team"]

# Build ordered Y-axis list respecting team_order
y_order = []
for team in team_order:
    offsets = sorted(df[df["Team"] == team]["Offset"].unique())
    for offset in offsets:
        y_order.append(f"{team} ({offset})")
y_order.reverse()

# Plot
fig = px.timeline(df,
                  x_start="Start",
                  x_end="End",
                  y="Y",
                  color="ColorGroup",
                  text="Lead",
                  category_orders={"Y": y_order},
                  color_discrete_map=team_color_map
                  )

fig.update_yaxes(autorange="reversed")
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    title="UBC Solar Team Lead Timeline",
    showlegend=False,
    )

fig.show()
