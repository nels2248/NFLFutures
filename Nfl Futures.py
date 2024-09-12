import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
from datetime import datetime 

# Load the Excel file
file_path = 'Nfl Futures 2024.xlsx'# Replace with your actual file path
df = pd.read_excel(file_path)

#Load colors file
file_path_teams = 'TeamColors.xlsx'# Replace with your actual file path
df_teams = pd.read_excel(file_path_teams)

#Join to colors
df = pd.merge(df, df_teams, on='TEAM', how='left')

# Clean the Color column (optional)
df['Color'] = df['Color'].str.strip().str.upper()

df['OriginalOdds'] = df['Odds']

maxodds = 3100
df['Odds'] = df['Odds'].apply(lambda x: maxodds if x > maxodds else x)


# Group the data by team
teams = df['TEAM'].unique()

# Assuming df is your DataFrame
# Sort the DataFrame by 'OriginalOdds' and 'TEAM'
df = df.sort_values(by=['OriginalOdds', 'TEAM'], ascending=[True, True])

# Rank within each group of 'Odds' and 'Week'
df['rank'] = df.groupby(['Odds', 'Week']).cumcount() + 1


df['rank_value'] = df['rank']-1

offset_increment = .05# Adjust as needed# Track the last position used to detect overlaps

df['Week'] = df['Week']+df['rank_value']*offset_increment

# Create the plot
plt.figure(figsize=(20, 8))
 
# Define the path to the logos folder
logo_folder = 'NflLogos'# Replace with your actual logos folder path# Plot each team's odds over the weeks and add logos

last_positions = {}

for team in teams:
    team_data = df[df['TEAM'] == team]
    team_color = df[df['TEAM'] == team]['Color'].values[0]
    plt.plot(team_data['Week'], team_data['Odds'], label=team, color=team_color)
    

    # Get the corresponding logo from the TEAM Column
    team_logo = team_data['TEAM'].iloc[0]  # Assuming the logo name is consistent for each team
    logo_path = os.path.join(logo_folder, f'{team_logo}.png')

    if os.path.exists(logo_path):
        for (x, y, rank, originalodds, color) in zip(team_data['Week'], team_data['Odds'], team_data['rank_value'], team_data['OriginalOdds'], team_data['Color']):
            img = mpimg.imread(logo_path)
            imagebox = OffsetImage(img, zoom=0.1)  # Adjust zoom to control the size of logos
            print(x,y,logo_path)
            ab = AnnotationBbox(imagebox, (x, y), frameon=False)
            plt.gca().add_artist(ab)
            # Format the odds with thousands separator 
            if originalodds > maxodds:
                plt.text(x, y+75,  f"${originalodds:,}", ha='center', fontsize=10, color=color, rotation=90)  # Adjust y+100 for placement above the image
            else:
                plt.text(x, y+15,  f"${y:,}", ha='center', fontsize=11, fontweight='bold', color=color, rotation=22.55)  # Adjust y+100 for placement above the image


    else:
        print(team_data['TEAM'])

# Add labels and title
plt.xlabel('Week')
plt.ylabel('Odds')
plt.title('NFL $100 Bet For Super Bowl Payout By Week 2024 Season')
#plt.legend(title='Teams', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.ylim(0,3500)
#plt.xlim(1,2.7)
# Set x-axis to show only the numbers we have
plt.xticks([1,2])

# Save the plot with date and time in the filename
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
plt.tight_layout()

#cursor.save_to_html('plot.html')
plt.savefig(f'NFL_Futures_Odds{timestamp}.png', dpi=300)

# Show the plot
plt.tight_layout()
plt.show()