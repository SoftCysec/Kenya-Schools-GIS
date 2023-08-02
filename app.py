import os
import geopandas as gpd
from flask import Flask, redirect, render_template, request, session, url_for
import dotenv
import folium

# call dotenv and it will automatically parse .env file and add them to environment variable
dotenv.load_dotenv()

app = Flask(__name__)  
app.secret_key = os.getenv("SECRET_KEY")

# Directory path where shapefile and associated files are located
data_dir = "Schools"
shapefile_path = os.path.join(data_dir, "Schools.shp")

# Load the shapefile data and create a spatial index
try:
    schools_data = gpd.read_file(shapefile_path)
    schools_data.sindex  # Create the spatial index
except FileNotFoundError:
    print(f"Shapefile '{shapefile_path}' not found. Please ensure the correct file path.")
    exit(1)

# Number of schools to display per page
schools_per_page = 10


@app.route("/")
def index():
    page = request.args.get("page", default=1, type=int)

    # Retrieve the search input from the session
    search_input = session.get("search_input")

    # If there is a search input, filter the data accordingly
    if search_input:
        filtered_schools_data = schools_data[
            schools_data["SCHOOL_NAM"].str.lower().str.contains(search_input.lower())
        ]
    else:
        filtered_schools_data = schools_data

    # Calculate the total number of pages for pagination
    total_pages = (len(filtered_schools_data) - 1) // schools_per_page + 1

    # Calculate the start and end index for the current page
    start_idx = (page - 1) * schools_per_page
    end_idx = start_idx + schools_per_page

    # Get the subset of schools to display on the current page
    schools_to_display = filtered_schools_data.iloc[start_idx:end_idx]

    # Calculate start and end pages for pagination
    start_page = max(page - 2, 1)
    end_page = min(start_page + 4, total_pages)

    return render_template(
        "index.html",
        schools=schools_to_display,
        current_page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page,
    )


@app.route("/search", methods=["POST"])
def search():
    # Get the search input from the form submission
    search_input = request.form.get("search-input", "").strip()

    # Store the search input in the session
    session["search_input"] = search_input

    # Redirect back to the index page with the updated search
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
