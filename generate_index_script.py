import pandas as pd
from pyvis.network import Network
import itertools

# 1. Load and Prepare the Data
df = pd.read_csv('IS82 Maps - IS82 Maps.csv')

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
        pairs = list(itertools.combinations(sorted(authors_in_map), 2))
        collaborations.extend(pairs)

# 2. Calculate Metrics for the Graph
author_counts = pd.Series(all_authors).value_counts()
edge_counts = pd.Series(collaborations).value_counts()

# 3. Create the Interactive Graph using Pyvis
net = Network(height='1000px', width='100%', bgcolor='#222222', font_color='white', notebook=False)

# Define explicit base colors 
base_node_color = "#5a9bd4"
base_edge_color = "rgba(170, 170, 170, 0.3)"

# 4. Set Global Options 
# - Removed edge fonts to restore high framerate.
# - Added a semi-transparent dark "background" to the node fonts to improve readability 
#   when edges pass behind the author names.
options = f"""
var options = {{
  "interaction": {{
    "hover": true,
    "selectConnectedEdges": true
  }},
  "nodes": {{
    "shape": "dot",
    "font": {{
      "size": 200,
      "face": "Arial",
      "strokeWidth": 8,
      "strokeColor": "#222222",
      "background": "rgba(34, 34, 34, 0.8)"
    }}
  }},
  "edges": {{
    "color": {{
      "color": "{base_edge_color}",
      "highlight": "rgba(255, 255, 255, 0.5)",
      "hover": "rgba(255, 255, 255, 0.5)"
    }},
    "smooth": {{
      "type": "continuous"
    }}
  }},
  "physics": {{
    "solver": "repulsion",
    "repulsion": {{
      "nodeDistance": 3000,
      "centralGravity": 0.01,
      "springLength": 3000,
      "springConstant": 0.005,
      "damping": 0.09
    }},
    "minVelocity": 0.75
  }}
}}
"""
net.set_options(options)

# Add Nodes (Authors)
for author, count in author_counts.items():
    node_size = 50 + (count * 5)
    
    net.add_node(
        author, 
        label=author, 
        title=f"Author: {author}\nTotal Maps: {count}", 
        size=node_size,
        color=base_node_color
    )

# Add Edges (Collaborations)
for (author1, author2), weight in edge_counts.items():
    edge_thickness = weight * 15 
    
    # - Removed the 'label' attribute to fix the framerate drop.
    net.add_edge(
        author1, 
        author2, 
        width=edge_thickness, 
        title=f"Joint Collaborations: {weight}",
        color=base_edge_color
    )

# 5. Generate the Base HTML File
html_filename = 'index.html'
net.write_html(html_filename)

# 6. Inject Custom CSS and JavaScript
# - Removed edge font logic from JS.
# - Updated node font logic to manage the 'background' property during select/deselect.
custom_injection = f"""
<style type="text/css">
    #mynetwork {{
        border: none !important;
        outline: none !important;
    }}
</style>

<script type="text/javascript">
    var defaultNodeColor = "{base_node_color}";
    var defaultEdgeColor = "{base_edge_color}";

    network.on("selectNode", function(params) {{
        if (params.nodes.length === 1) {{
            var selectedNode = params.nodes[0];
            var connectedNodes = network.getConnectedNodes(selectedNode);
            var allNodes = nodes.get();
            var allEdges = edges.get();
            
            for (var i = 0; i < allNodes.length; i++) {{
                if (allNodes[i].id !== selectedNode && !connectedNodes.includes(allNodes[i].id)) {{
                    allNodes[i].color = "rgba(100, 100, 100, 0.08)";
                    // Remove the background pill for unselected nodes to declutter the view
                    allNodes[i].font = {{ color: "rgba(255, 255, 255, 0.08)", strokeColor: "rgba(0, 0, 0, 0.05)", strokeWidth: 8, background: "rgba(34, 34, 34, 0.0)" }};
                }} else {{
                    allNodes[i].color = defaultNodeColor; 
                    // Maintain the background pill for active nodes
                    allNodes[i].font = {{ color: "rgba(255, 255, 255, 1)", strokeColor: "#222222", strokeWidth: 8, background: "rgba(34, 34, 34, 0.8)" }};
                }}
            }}
            
            for (var j = 0; j < allEdges.length; j++) {{
                if (allEdges[j].from === selectedNode || allEdges[j].to === selectedNode) {{
                    allEdges[j].color = {{ color: "rgba(255, 255, 255, 0.5)", highlight: "rgba(255, 255, 255, 0.6)" }};
                }} else {{
                    allEdges[j].color = {{ color: "rgba(170, 170, 170, 0.05)" }}; 
                }}
            }}
            
            nodes.update(allNodes);
            edges.update(allEdges);
        }}
    }});

    network.on("deselectNode", function(params) {{
        var allNodes = nodes.get();
        var allEdges = edges.get();
        
        for (var i = 0; i < allNodes.length; i++) {{
            allNodes[i].color = defaultNodeColor;
            // Restore the background pill for all nodes
            allNodes[i].font = {{ color: "rgba(255, 255, 255, 1)", strokeColor: "#222222", strokeWidth: 8, background: "rgba(34, 34, 34, 0.8)" }};
        }}
        
        for (var j = 0; j < allEdges.length; j++) {{
            allEdges[j].color = defaultEdgeColor;
        }}
        
        nodes.update(allNodes);
        edges.update(allEdges);
    }});
</script>
"""

with open(html_filename, 'a', encoding='utf-8') as f:
    f.write(custom_injection)

print("Interactive graph generated successfully. Framerate restored and node text readability enhanced.")