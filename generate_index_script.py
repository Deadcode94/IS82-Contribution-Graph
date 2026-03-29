import pandas as pd
from pyvis.network import Network
import itertools
import json

# 1. Load and Prepare the Data
df = pd.read_csv('IS82 Maps - IS82 Maps.csv')

def get_parsed_authors(row):
    primary = []
    collaborators = []
    
    # Extract primary author(s)
    if pd.notna(row['Author']):
        primary.extend([a.strip() for a in str(row['Author']).split(',') if a.strip()])
        
    # Extract co-authors
    if pd.notna(row['Other Authors']):
        collaborators.extend([a.strip() for a in str(row['Other Authors']).split(',') if a.strip()])
        
    return primary, collaborators

# Create lists and dictionaries to track all graph metrics
collaborations = []
all_authors = []
author_maps_data = {}
author_years = {}

for idx, row in df.iterrows():
    map_name = str(row['Name']).strip()
    map_year = int(row['Year']) if pd.notna(row['Year']) else 2004
    
    primary_authors, collaborator_authors = get_parsed_authors(row)
    combined_authors = primary_authors + collaborator_authors
    all_authors.extend(combined_authors)
    
    # Track complex map data (Name, Year, Role) for the frontend UI
    for author in primary_authors:
        if author not in author_maps_data:
            author_maps_data[author] = []
            author_years[author] = []
        
        # Prevent duplicates if data is messy
        if not any(m['name'] == map_name for m in author_maps_data[author]):
            author_maps_data[author].append({'name': map_name, 'year': map_year, 'role': 'Primary'})
        author_years[author].append(map_year)
        
    for author in collaborator_authors:
        if author not in author_maps_data:
            author_maps_data[author] = []
            author_years[author] = []
            
        if not any(m['name'] == map_name for m in author_maps_data[author]):
            author_maps_data[author].append({'name': map_name, 'year': map_year, 'role': 'Collaborator'})
        author_years[author].append(map_year)
    
    # If there are at least two authors in total, create collaboration pairs
    if len(combined_authors) > 1:
        pairs = list(itertools.combinations(sorted(combined_authors), 2))
        collaborations.extend(pairs)

# Convert the complex dictionary to JSON to inject it into JS later
author_maps_json = json.dumps(author_maps_data)

# 2. Calculate Metrics for the Graph
author_counts = pd.Series(all_authors).value_counts()
edge_counts = pd.Series(collaborations).value_counts()

# 3. Create the Interactive Graph using Pyvis
net = Network(height='100vh', width='100%', bgcolor='#222222', font_color='white', notebook=False)

base_edge_color = "rgba(170, 170, 170, 0.3)"

# 4. Set Global Options 
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

# Add Nodes (Authors) with Era Colors
for author, count in author_counts.items():
    node_size = 50 + (count * 5)
    
    min_year = min(author_years[author])
    max_year = max(author_years[author])
    activity_period = f"{min_year}-{max_year}" if min_year != max_year else f"{min_year}"
    
    if min_year <= 2007:
        era_color = "#ffd700"  # Gold
    elif min_year <= 2012:
        era_color = "#20b2aa"  # Teal
    else:
        era_color = "#9370db"  # Purple
        
    hover_text = (
        f"Author: {author}\n"
        f"Active: {activity_period}\n"
        f"Total Contributions: {count}\n"
        f"(Click to see details)"
    )
    
    net.add_node(
        author, 
        label=author, 
        title=hover_text, 
        size=node_size,
        color=era_color
    )

# Add Edges (Collaborations)
for (author1, author2), weight in edge_counts.items():
    edge_thickness = weight * 15 
    
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

# 6. Inject Custom CSS, HTML UI, and JavaScript
custom_injection = f"""
<style type="text/css">
    body, html {{ margin: 0; padding: 0; overflow: hidden; font-family: Arial, sans-serif; }}
    #mynetwork {{ border: none !important; outline: none !important; height: 100vh !important; }}
    
    #custom-ui-panel {{
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 1000;
        background: rgba(20, 20, 20, 0.9);
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #444;
        color: white;
        width: 320px; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        max-height: 90vh;
        display: flex;
        flex-direction: column;
    }}
    #custom-ui-panel h3 {{ margin-top: 0; font-size: 16px; border-bottom: 1px solid #555; padding-bottom: 10px; }}
    #custom-ui-panel h4 {{ font-size: 14px; margin: 15px 0 5px 0; }}
    #author-search {{ width: 100%; padding: 8px; margin-bottom: 15px; background: #333; color: white; border: 1px solid #555; border-radius: 4px; }}
    #freeze-btn {{ width: 100%; padding: 10px; cursor: pointer; background: #5a9bd4; color: white; border: none; border-radius: 4px; font-weight: bold; transition: background 0.2s; }}
    #freeze-btn:hover {{ background: #4a8bc4; }}
    .legend-list {{ list-style: none; padding: 0; margin: 0; font-size: 13px; line-height: 1.8; }}
    .legend-color {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }}
    
    /* Dynamic details section */
    #author-details {{
        display: none;
        margin-top: 15px;
        border-top: 1px solid #555;
        padding-top: 15px;
        flex-grow: 1;
        overflow: hidden;
        flex-direction: column;
    }}
    #detail-name {{ margin-top: 0; color: #5a9bd4; font-size: 15px; margin-bottom: 10px; }}
    #sort-maps {{ width: 100%; padding: 5px; margin-bottom: 10px; background: #222; color: #ddd; border: 1px solid #555; border-radius: 4px; font-size: 12px; }}
    
    #detail-maps-container {{
        overflow-y: auto;
        padding-right: 5px;
        flex-grow: 1;
        max-height: 35vh; 
    }}
    #detail-maps-container::-webkit-scrollbar {{ width: 6px; }}
    #detail-maps-container::-webkit-scrollbar-track {{ background: #222; border-radius: 3px; }}
    #detail-maps-container::-webkit-scrollbar-thumb {{ background: #555; border-radius: 3px; }}
    #detail-maps-container::-webkit-scrollbar-thumb:hover {{ background: #777; }}
    
    .map-item {{ font-size: 13px; margin-bottom: 6px; color: #ddd; display: flex; align-items: flex-start; }}
    
    /* New styling for AUTHOR and COLLAB tags */
    .author-tag {{ color: #e74c3c; font-size: 10px; font-weight: bold; margin-right: 5px; padding-top: 2px; flex-shrink: 0; }}
    .collab-tag {{ color: #888888; font-size: 10px; font-weight: bold; margin-right: 5px; padding-top: 2px; flex-shrink: 0; }}
</style>

<div id="custom-ui-panel">
    <div>
        <h3>IS82 Modding Network</h3>
        <select id="author-search">
            <option value="">-- Search Author --</option>
        </select>
        <button id="freeze-btn">Freeze Graph Physics</button>
        
        <h4>Eras (First Map)</h4>
        <ul class="legend-list">
            <li><span class="legend-color" style="background: #ffd700;"></span> Veterans (<= 2007)</li>
            <li><span class="legend-color" style="background: #20b2aa;"></span> 2nd Gen (2008-2012)</li>
            <li><span class="legend-color" style="background: #9370db;"></span> New Era (>= 2013)</li>
        </ul>
        
        <h4>Metrics</h4>
        <ul class="legend-list">
            <li>◯ Node Size = Contributions</li>
            <li>━ Thickness = Collaborations</li>
        </ul>
    </div>
    
    <div id="author-details" style="display: none;">
        <h4 id="detail-name"></h4>
        
        <select id="sort-maps">
            <option value="year">Sort by Release Year (Oldest First)</option>
            <option value="name">Sort Alphabetically (A-Z)</option>
        </select>
        
        <div id="detail-maps-container">
            <ul id="detail-maps" class="legend-list"></ul>
        </div>
    </div>
</div>

<script type="text/javascript">
    var defaultEdgeColor = "{base_edge_color}";
    var originalColors = {{}};
    // Complex JSON containing name, year, and role for each map
    var authorMapsData = {author_maps_json};
    var currentSelectedNode = null;

    // Function to render the map list based on the selected sort criteria
    function renderMapList() {{
        if (!currentSelectedNode) return;
        
        var maps = authorMapsData[currentSelectedNode].slice(); // clone array
        var sortType = document.getElementById('sort-maps').value;
        
        // Sorting logic
        maps.sort(function(a, b) {{
            if (sortType === 'year') {{
                if (a.year !== b.year) return a.year - b.year; // Sort by year
                return a.name.localeCompare(b.name);           // Fallback to name if same year
            }} else {{
                return a.name.localeCompare(b.name);           // Sort purely by name
            }}
        }});
        
        var mapsListEl = document.getElementById('detail-maps');
        mapsListEl.innerHTML = ""; 
        
        // Render each item
        maps.forEach(function(m) {{
            var li = document.createElement('li');
            li.className = 'map-item';
            
            // Add visual tags based on their specific role in this map
            var prefix = "";
            if (m.role === 'Primary') {{
                prefix = "<span class='author-tag'>[AUTHOR]</span>";
            }} else if (m.role === 'Collaborator') {{
                prefix = "<span class='collab-tag'>[COLLAB]</span>";
            }}
            
            var textContent = "<span>" + m.name + " (" + m.year + ")</span>";
            li.innerHTML = prefix + textContent;
            mapsListEl.appendChild(li);
        }});
    }}

    // Re-render the list immediately if the user changes the sort dropdown
    document.getElementById('sort-maps').addEventListener('change', renderMapList);

    setTimeout(function() {{
        nodes.get().forEach(function(n) {{
            originalColors[n.id] = n.color.background || n.color;
        }});

        var select = document.getElementById('author-search');
        var nodeIds = nodes.getIds();
        nodeIds.sort(function(a, b) {{ return a.toLowerCase().localeCompare(b.toLowerCase()); }});
        
        nodeIds.forEach(function(id) {{
            var opt = document.createElement('option');
            opt.value = id;
            opt.innerHTML = id;
            select.appendChild(opt);
        }});

        select.addEventListener('change', function() {{
            var selectedId = this.value;
            if (selectedId) {{
                network.focus(selectedId, {{
                    scale: 0.2, 
                    animation: {{ duration: 1000, easingFunction: 'easeInOutQuad' }}
                }});
                network.selectNodes([selectedId]);
                network.emit('selectNode', {{ nodes: [selectedId] }});
            }} else {{
                network.unselectAll();
                network.emit('deselectNode', {{}});
                network.fit({{ animation: {{ duration: 1000 }} }});
            }}
        }});

        var freezeBtn = document.getElementById('freeze-btn');
        freezeBtn.addEventListener('click', function() {{
            var isPhysicsEnabled = network.physics.options.enabled;
            network.setOptions({{ physics: {{ enabled: !isPhysicsEnabled }} }});
            
            if (isPhysicsEnabled) {{
                this.innerText = "Unfreeze Graph Physics";
                this.style.background = "#d45a5a";
            }} else {{
                this.innerText = "Freeze Graph Physics";
                this.style.background = "#5a9bd4";
            }}
        }});
    }}, 1000);

    network.on("selectNode", function(params) {{
        if (params.nodes.length === 1) {{
            var selectedNode = params.nodes[0];
            currentSelectedNode = selectedNode; // Track global state for sorting updates
            
            var connectedNodes = network.getConnectedNodes(selectedNode);
            var allNodes = nodes.get();
            var allEdges = edges.get();
            
            // Highlight/Fade nodes
            for (var i = 0; i < allNodes.length; i++) {{
                if (allNodes[i].id !== selectedNode && !connectedNodes.includes(allNodes[i].id)) {{
                    allNodes[i].color = "rgba(100, 100, 100, 0.08)";
                    allNodes[i].font = {{ color: "rgba(255, 255, 255, 0.08)", strokeColor: "rgba(0, 0, 0, 0.05)", strokeWidth: 8, background: "rgba(34, 34, 34, 0.0)" }};
                }} else {{
                    allNodes[i].color = originalColors[allNodes[i].id]; 
                    allNodes[i].font = {{ color: "rgba(255, 255, 255, 1)", strokeColor: "#222222", strokeWidth: 8, background: "rgba(34, 34, 34, 0.8)" }};
                }}
            }}
            
            // Highlight/Fade edges
            for (var j = 0; j < allEdges.length; j++) {{
                if (allEdges[j].from === selectedNode || allEdges[j].to === selectedNode) {{
                    allEdges[j].color = {{ color: "rgba(255, 255, 255, 0.5)", highlight: "rgba(255, 255, 255, 0.6)" }};
                }} else {{
                    allEdges[j].color = {{ color: "rgba(170, 170, 170, 0.05)" }}; 
                }}
            }}
            
            nodes.update(allNodes);
            edges.update(allEdges);

            // Update UI Panel Display
            var detailsContainer = document.getElementById('author-details');
            var nameEl = document.getElementById('detail-name');
            
            nameEl.innerText = selectedNode + "'s Contributions (" + authorMapsData[selectedNode].length + ")";
            
            // Call the shared render function
            renderMapList();
            
            detailsContainer.style.display = "flex";
        }}
    }});

    network.on("deselectNode", function(params) {{
        currentSelectedNode = null; // Clear tracking
        
        var allNodes = nodes.get();
        var allEdges = edges.get();
        
        for (var i = 0; i < allNodes.length; i++) {{
            allNodes[i].color = originalColors[allNodes[i].id];
            allNodes[i].font = {{ color: "rgba(255, 255, 255, 1)", strokeColor: "#222222", strokeWidth: 8, background: "rgba(34, 34, 34, 0.8)" }};
        }}
        
        for (var j = 0; j < allEdges.length; j++) {{
            allEdges[j].color = defaultEdgeColor;
        }}
        
        nodes.update(allNodes);
        edges.update(allEdges);

        // Hide UI Panel details
        document.getElementById('author-details').style.display = "none";
    }});
</script>
"""

with open(html_filename, 'a', encoding='utf-8') as f:
    f.write(custom_injection)

print("Interactive graph generated successfully. Visual distinction between PRIMARY and COLLABORATOR added.")