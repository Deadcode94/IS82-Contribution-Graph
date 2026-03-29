# IS82 Modding Community Contribution Graph

This project generates a dynamic, interactive network graph that visualizes the collaborations between map authors in the IS82 modding community. It processes map data from a CSV file using a Python script and outputs a single, self-contained `index.html` file with a rich user interface for exploration.

!Graph Preview <!-- You can replace this with a real screenshot -->

## Features

*   **Interactive Network Graph:** Pan, zoom, and drag nodes (authors) to explore the network.
*   **Data-Driven Visuals:**
    *   **Node Size:** Proportional to the author's total number of contributions.
    *   **Edge Thickness:** Proportional to the number of joint collaborations between two authors.
*   **Era-Based Coloring:** Authors are color-coded based on the year of their first map, categorizing them into "Veterans," "2nd Gen," and "New Era."
*   **Detailed Side Panel:**
    *   **Author Search:** Quickly find and focus on any author in the graph.
    *   **Freeze Physics:** Lock the graph in place for easier inspection.
    *   **Contribution List:** Click an author to see a detailed, sortable list of all their maps (as both primary author and collaborator).
*   **Focus View:** When an author is selected, the graph automatically dims unconnected nodes to highlight their direct collaborators.
*   **Custom Logic:** Includes special logic to handle specific cases, such as adjusting an author's "era" to exclude historical map revamps and provide context in the UI.

## How It Works

The project is powered by a single Python script (`generate_index_script.py`) that performs the following steps:

1.  **Data Loading:** Reads map and author data from `IS82 Maps - IS82 Maps.csv` using the **Pandas** library.
2.  **Graph Generation:** Uses the **Pyvis** library to create the underlying network graph structure and generate a base HTML file.
3.  **UI Injection:** Injects a large block of custom **HTML, CSS, and JavaScript** into the Pyvis output. This creates the final interactive UI, including the side panel, search functionality, and dynamic event handling (like clicking a node).

The final result is a single `index.html` file that requires no backend or external dependencies to run.

## Setup and Usage

### 1. Prerequisites

*   Python 3.6+
*   A CSV file named `IS82 Maps - IS82 Maps.csv` located in the same directory as the script.

### 2. Data Format

The script expects the CSV file to have at least the following columns. The script is designed to be robust against missing data.

*   `Name`: The name of the map.
*   `Year`: The year the map was released.
*   `Author`: A comma-separated string of the primary author(s).
*   `Other Authors`: A comma-separated string of any collaborating or co-author(s).

### 3. Installation

First, it's recommended to create a virtual environment for the project. Then, install the required Python libraries from your terminal:

```bash
pip install pandas pyvis
```

You can also create a `requirements.txt` file with the following content and run `pip install -r requirements.txt`:

```
pandas
pyvis
```

### 4. Running the Script

With your `IS82 Maps - IS82 Maps.csv` file in place, execute the Python script from your terminal:

```bash
python generate_index_script.py
```

### 5. Viewing the Output

The script will generate (or overwrite) a file named `index.html` in the same directory. Simply open this file in any modern web browser to view and interact with the contribution graph.

## Customization

The script and the injected code can be easily modified:

*   **Era Colors & Thresholds:** The year ranges and color codes for the different eras are defined directly in the `generate_index_script.py` file within the main node-creation loop.
*   **UI Text & Styling:** All UI elements, text, and styles are located in the `custom_injection` string at the end of the Python script. You can modify the HTML, CSS, and JavaScript here to change the appearance and functionality of the side panel.
*   **Graph Physics:** The physics properties (like repulsion, gravity, and spring length) are configured in the `options` string within the Python script. You can tweak these values to change how the graph nodes behave.