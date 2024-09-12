# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 19:48:11 2024

@author: nels2
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import base64
from PIL import Image

# Load the data
futures_data = pd.read_excel('NFL Futures 2024.xlsx')
color_data = pd.read_excel('TeamColors.xlsx')

# Merge the futures data with the team colors
merged_data = pd.merge(futures_data, color_data, on='TEAM')

# Function to get base64 encoded team logo
def get_team_logo_base64(team_name):
    logo_path = os.path.join('NFLLogos', f'{team_name}.png')
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode()
            return base64_image
    else:
        st.warning(f"Logo not found for team: {team_name}")
    return None

# Set up the Streamlit page
st.title('NFL Super Bowl Payout on $100 Bet in Vegas')

# Sidebar filters
st.sidebar.header('Filters')

# Filter by Odds
min_odds_input = st.sidebar.text_input(
    'Minimum Payout',
    value=str(float(merged_data['Odds'].min()))
)
max_odds_input = st.sidebar.text_input(
    'Maximum Payout',
    value=str(float(merged_data['Odds'].max()))
)

# Convert inputs to float and handle invalid inputs
try:
    min_odds = float(min_odds_input)
    max_odds = float(max_odds_input)
except ValueError:
    st.error("Please enter valid numeric values for Odds.")
    min_odds = float(merged_data['Odds'].min())
    max_odds = float(merged_data['Odds'].max())

# Filter by Teams
all_teams = sorted(merged_data['TEAM'].unique())  # Sorted list of teams

# Add Select All option
select_all = st.sidebar.checkbox('Select All Teams', value=True)

selected_teams = []

if select_all:
    selected_teams = all_teams
else:
    for team in all_teams:
        if st.sidebar.checkbox(team, value=False):
            selected_teams.append(team)

# Apply filters to the data
filtered_data = merged_data[
    (merged_data['Odds'] >= min_odds) &
    (merged_data['Odds'] <= max_odds) &
    (merged_data['TEAM'].isin(selected_teams))
]

# Initialize plotly figure
fig = go.Figure()

# Create a combined hover text dictionary to track multiple teams for the same Odds/Week
hover_dict = {}

# Add a line for each team
for team in selected_teams:
    team_data = filtered_data[filtered_data['TEAM'] == team]
    
    if team_data.empty:
        continue  # Skip if no data for this team
    
    color = team_data['Color'].iloc[0] if 'Color' in team_data.columns else '#000000'  # Default to black if Color is missing

    # Add the line for the team
    fig.add_trace(go.Scatter(
        x=team_data['Week'],
        y=team_data['Odds'],
        mode='lines+markers',
        name=team,
        line=dict(color=color),
        hoverinfo='text',
        text=[f'Team: {team}<br>Odds: {odds}<br>Week: {week}'
              for odds, week in zip(team_data['Odds'], team_data['Week'])]
    ))

    # Add logos as custom data points
    for _, row in team_data.iterrows():
        week = row['Week']
        odds = row['Odds']
        logo_base64 = get_team_logo_base64(team)

        # Add multiple teams into hover_dict for combined hover effect
        hover_key = (week, odds)
        if hover_key not in hover_dict:
            hover_dict[hover_key] = []
        hover_dict[hover_key].append(team)

        if logo_base64:
            fig.add_layout_image(
                dict(
                    source=f'data:image/png;base64,{logo_base64}',  # Use base64 encoded string
                    x=week,  # x position (Week)
                    y=odds,  # y position (Odds)
                    xref="x",  # x-axis reference
                    yref="y",  # y-axis reference
                    sizex=.1,  # Small size for x-axis
                    sizey=1750,  # Adjusted size for large y-axis
                    xanchor="center",  # Center the image at the data point
                    yanchor="middle",  # Center the image at the data point
                    opacity=1,
                    layer="above"  # Draw image above the plot
                )
            )

# Modify hover text to show all teams for the same Odds/Week combination
hover_text_combined = [
    f"Teams: {', '.join(hover_dict[(week, odds)])}<br>Odds: {odds}<br>Week: {week}"
    for week, odds in hover_dict
]

# Add a dummy trace to show combined hover info at common points
fig.add_trace(go.Scatter(
    x=[week for week, odds in hover_dict.keys()],
    y=[odds for week, odds in hover_dict.keys()],
    mode='markers',
    marker=dict(color='rgba(255,255,255,0)'),
    hoverinfo='text',
    text=hover_text_combined,
    showlegend=False  # Don't show this in the legend
))

# Customize layout for interactivity
fig.update_layout(
    title='NFL Super Bowl Payout on $100 Bet in Vegas',
    xaxis_title='Week',
    yaxis_title='Odds',
    hovermode='closest',
    showlegend=False  # Removes legend
)

# Display the interactive plot
st.plotly_chart(fig)
