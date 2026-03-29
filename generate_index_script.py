import pandas as pd
from pyvis.network import Network
import itertools

# 1. Load and Prepare the Data
# Ensure the CSV file is in the same directory as the script
df = pd.read_csv('IS82 Maps - IS82 Maps.csv')

# Function to clean and retrieve the list of authors from a row
def get_authors(row):
    authors = []
    # Extract primary author(s)
    if pd.notna(row['Author']):
        authors.extend([a.strip() for a in str(row['Author']).split(',')])
    # Extract co-authors
    if pd.notna(row['Other Authors']):
        authors.extend([a.strip() for a in str(row['Other Authors']).split(',')])
        
    # Remove any empty strings
    return [a for a in authors if a]

# Create lists to track all individual authors and unique collaboration pairs
collaborations = []
all_authors = []

for idx, row in df.iterrows():
    authors_in_map = get_authors(row)
    all_authors.extend(authors_in_map)
    
    # If there are at least two authors, create collaboration pairs
    if len(authors_in_map) > 1:
        # itertools.combinations creates all unique pairs possible: (A,B), (A,C), (B,C)
        pairs = list(itertools.combinations(sorted(authors_in_map), 2))
        collaborations.extend(pairs)

# 2. Calculate Metrics for the Graph
# Count the total number of maps per author (used for node size)
author_counts = pd.Series(all_authors).value_counts()

# Count how many times each pair collaborated (used for edge thickness)
edge_counts = pd.Series(collaborations).value_counts()

# 3. Create the Interactive Graph using Pyvis
net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white', notebook=False)

# Add Nodes (Authors)
for author, count in author_counts.items():
    # Node size is proportional to the number of maps contributed
    net.add_node(author, label=author, title=f"Author: {author}\nTotal Maps: {count}", size=count*2)

# Add Edges (Collaborations)
for (author1, author2), weight in edge_counts.items():
    # Edge value defines its thickness based on the number of joint collaborations
    net.add_edge(author1, author2, value=weight, title=f"Joint Collaborations: {weight}")

# Configure physics for an optimal force-directed layout
net.barnes_hut()

# Save the graph to an HTML file instead of trying to show it in a notebook environment
net.save_graph('index.html')

print("Interactive graph generated successfully as 'index.html'. Ready for GitHub Pages deployment.")
