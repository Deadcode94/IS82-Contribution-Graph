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
all_maps_data = {}

for idx, row in df.iterrows():
    map_name = str(row['Name']).strip()
    map_year = int(row['Year']) if pd.notna(row['Year']) else 2004
    
    primary_authors, collaborator_authors = get_parsed_authors(row)
    combined_authors = primary_authors + collaborator_authors
    all_authors.extend(combined_authors)
    
    # Store global map data
    if map_name not in all_maps_data:
        all_maps_data[map_name] = {
            'name': map_name,
            'year': map_year,
            'primary_authors': primary_authors,
            'collaborators': collaborator_authors
        }
    else:
        all_maps_data[map_name]['primary_authors'] = list(set(all_maps_data[map_name]['primary_authors'] + primary_authors))
        all_maps_data[map_name]['collaborators'] = list(set(all_maps_data[map_name]['collaborators'] + collaborator_authors))
        
    # Track complex map data (Name, Year, Role) for the frontend UI
    for i, author in enumerate(primary_authors):
        if author not in author_maps_data:
            author_maps_data[author] = []
            author_years[author] = []
        
        # Prevent duplicates if data is messy
        if not any(m['name'] == map_name for m in author_maps_data[author]):
            author_maps_data[author].append({'name': map_name, 'year': map_year, 'role': 'Primary', 'is_first_author': i == 0})
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
all_maps_json = json.dumps(all_maps_data)

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
    
    # Goodday Era Logic Override
    if author == "GoodDayToDie!!":
        primary_years = [m['year'] for m in author_maps_data.get(author, []) if m['role'] == 'Primary' and m.get('is_first_author', False)]
        min_year = min(primary_years) if primary_years else min(author_years[author])
    else:
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
    body, html {{ 
        margin: 0 !important; 
        padding: 0 !important; 
        width: 100% !important;
        height: 100% !important;
        background-color: #222222 !important; 
        overflow: hidden !important; 
        font-family: Arial, sans-serif; 
    }}
    
    center, .card, .container, .container-fluid {{
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        background: none !important;
        background-color: #222222 !important;
        max-width: 100% !important;
    }}
    
    #mynetwork {{ 
        width: 100vw !important;
        height: 100vh !important; 
        border: none !important; 
        border-radius: 0 !important; 
        outline: none !important; 
        margin: 0 !important;
        padding: 0 !important;
        background-color: #222222 !important; 
    }}
    
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
        box-sizing: border-box;
    }}
    #custom-ui-panel h3 {{ margin-top: 0; font-size: 16px; border-bottom: 1px solid #555; padding-bottom: 10px; }}
    #custom-ui-panel h4 {{ font-size: 14px; margin: 15px 0 5px 0; }}
    #author-search, #map-search {{ width: 100%; padding: 8px; margin-bottom: 15px; background: #333; color: white; border: 1px solid #555; border-radius: 4px; box-sizing: border-box; }}
    #freeze-btn {{ width: 100%; padding: 10px; cursor: pointer; background: #5a9bd4; color: white; border: none; border-radius: 4px; font-weight: bold; transition: background 0.2s; box-sizing: border-box; }}
    #freeze-btn:hover {{ background: #4a8bc4; }}
    .legend-list {{ list-style: none; padding: 0; margin: 0; font-size: 13px; line-height: 1.8; }}
    .legend-color {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }}
    
    #author-details {{
        display: none;
        margin-top: 15px;
        border-top: 1px solid #555;
        padding-top: 15px;
        flex-grow: 1;
        overflow: hidden;
        flex-direction: column;
    }}
    
    /* Title and Subtitle Styling */
    #detail-name {{ margin-top: 0; margin-bottom: 5px; color: #5a9bd4; font-size: 15px; }}
    #detail-subtitle {{ display: none; font-size: 11px; font-style: italic; color: #aaa; margin-bottom: 10px; line-height: 1.3; }}
    
    #sort-maps {{ width: 100%; padding: 5px; margin-bottom: 10px; background: #222; color: #ddd; border: 1px solid #555; border-radius: 4px; font-size: 12px; box-sizing: border-box; }}
    
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
    
    .map-item {{ font-size: 13px; margin-bottom: 6px; color: #ddd; display: flex; align-items: flex-start; cursor: pointer; transition: background 0.2s; padding: 3px; border-radius: 3px; }}
    .map-item:hover {{ background: rgba(255, 255, 255, 0.1); }}
    
    .author-tag {{ color: #e74c3c; font-size: 10px; font-weight: bold; margin-right: 5px; padding-top: 2px; flex-shrink: 0; }}
    .collab-tag {{ color: #888888; font-size: 10px; font-weight: bold; margin-right: 5px; padding-top: 2px; flex-shrink: 0; }}

    #map-details-modal {{
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(20, 20, 20, 0.95);
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #5a9bd4;
        color: white;
        z-index: 2000;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.8);
        min-width: 300px;
    }}
    #map-details-modal h3 {{ margin-top: 0; color: #5a9bd4; border-bottom: 1px solid #555; padding-bottom: 10px; }}
    #map-details-modal p {{ font-size: 14px; line-height: 1.5; margin: 8px 0; }}
    .close-modal-btn {{
        position: absolute;
        top: 10px;
        right: 15px;
        background: none;
        border: none;
        color: #aaa;
        font-size: 20px;
        cursor: pointer;
    }}
    .close-modal-btn:hover {{ color: white; }}

    #modal-backdrop {{
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.4); /* Slight dimming effect */
        z-index: 1500; /* Placed below the modal but above the UI and graph */
    }}
</style>

<div id="custom-ui-panel">
    <div>
        <h3>IS82 Modding Network</h3>
        <select id="author-search">
            <option value="">-- Search Author --</option>
        </select>
        <select id="map-search">
            <option value="">-- Search Map --</option>
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
        <div id="detail-subtitle"></div>
        
        <select id="sort-maps">
            <option value="year">Sort by Release Year (Oldest First)</option>
            <option value="name">Sort Alphabetically (A-Z)</option>
        </select>
        
        <div id="detail-maps-container">
            <ul id="detail-maps" class="legend-list"></ul>
        </div>
    </div>
</div>

<div id="map-details-modal">
    <button class="close-modal-btn" onclick="closeMapModal()">×</button>
    <h3 id="modal-map-name"></h3>
    <p><strong>Year:</strong> <span id="modal-map-year"></span></p>
    <p><strong>Primary Author(s):</strong> <span id="modal-map-primary"></span></p>
    <p><strong>Collaborator(s):</strong> <span id="modal-map-collab"></span></p>
</div>

<!-- Invisible/Dimmed overlay to catch outside clicks and prevent graph deselection -->
<div id="modal-backdrop" onclick="closeMapModal()"></div>

<script type="text/javascript">
    var defaultEdgeColor = "{base_edge_color}";
    var originalColors = {{}};
    var authorMapsData = {author_maps_json};
    var allMapsData = {all_maps_json};
    var currentSelectedNode = null;

    function showMapDetails(mapName) {{
        var mapData = allMapsData[mapName];
        if (!mapData) return;
        
        document.getElementById('modal-map-name').innerText = mapData.name;
        document.getElementById('modal-map-year').innerText = mapData.year;
        document.getElementById('modal-map-primary').innerText = mapData.primary_authors.length > 0 ? mapData.primary_authors.join(', ') : 'None';
        document.getElementById('modal-map-collab').innerText = mapData.collaborators.length > 0 ? mapData.collaborators.join(', ') : 'None';
        
        document.getElementById('map-details-modal').style.display = 'block';
        document.getElementById('modal-backdrop').style.display = 'block';
    }}

    function closeMapModal() {{
        document.getElementById('map-details-modal').style.display = 'none';
        document.getElementById('modal-backdrop').style.display = 'none';
        document.getElementById('map-search').value = "";
    }}

    function renderMapList() {{
        if (!currentSelectedNode) return;
        
        var maps = authorMapsData[currentSelectedNode].slice(); 
        var sortType = document.getElementById('sort-maps').value;
        
        maps.sort(function(a, b) {{
            if (sortType === 'year') {{
                if (a.year !== b.year) return a.year - b.year; 
                return a.name.localeCompare(b.name);           
            }} else {{
                return a.name.localeCompare(b.name);           
            }}
        }});
        
        var mapsListEl = document.getElementById('detail-maps');
        mapsListEl.innerHTML = ""; 
        
        maps.forEach(function(m) {{
            var li = document.createElement('li');
            li.className = 'map-item';
            li.onclick = function() {{ showMapDetails(m.name); }};
            
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

        var mapSelect = document.getElementById('map-search');
        var mapNames = Object.keys(allMapsData);
        mapNames.sort(function(a, b) {{ return a.toLowerCase().localeCompare(b.toLowerCase()); }});
        
        mapNames.forEach(function(name) {{
            var opt = document.createElement('option');
            opt.value = name;
            opt.innerHTML = name;
            mapSelect.appendChild(opt);
        }});

        mapSelect.addEventListener('change', function() {{
            var selectedMap = this.value;
            if (selectedMap) {{
                showMapDetails(selectedMap);
            }} else {{
                closeMapModal();
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
        closeMapModal();

        if (params.nodes.length === 1) {{
            var selectedNode = params.nodes[0];
            currentSelectedNode = selectedNode; 
            
            var connectedNodes = network.getConnectedNodes(selectedNode);
            var allNodes = nodes.get();
            var allEdges = edges.get();
            
            for (var i = 0; i < allNodes.length; i++) {{
                if (allNodes[i].id !== selectedNode && !connectedNodes.includes(allNodes[i].id)) {{
                    allNodes[i].color = "rgba(100, 100, 100, 0.08)";
                    allNodes[i].font = {{ color: "rgba(255, 255, 255, 0.08)", strokeColor: "rgba(0, 0, 0, 0.05)", strokeWidth: 8, background: "rgba(34, 34, 34, 0.0)" }};
                }} else {{
                    allNodes[i].color = originalColors[allNodes[i].id]; 
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

            var detailsContainer = document.getElementById('author-details');
            var nameEl = document.getElementById('detail-name');
            var subtitleEl = document.getElementById('detail-subtitle');
            
            nameEl.innerText = selectedNode + "'s Contributions (" + authorMapsData[selectedNode].length + ")";
            
            // Toggle subtitle logic specifically for Goodday
            if (selectedNode === 'GoodDayToDie!!') {{
                subtitleEl.innerHTML = "*Era based on original maps only, excluding historical revamps.";
                subtitleEl.style.display = "block";
            }} else {{
                subtitleEl.style.display = "none";
            }}
            
            renderMapList();
            
            detailsContainer.style.display = "flex";
        }}
    }});

    network.on("deselectNode", function(params) {{
        closeMapModal();

        currentSelectedNode = null; 
        
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

        document.getElementById('author-details').style.display = "none";
    }});
</script>
"""

with open(html_filename, 'a', encoding='utf-8') as f:
    f.write(custom_injection)

print("Interactive graph generated successfully. UI explanatory subtitle for Goodday added.")