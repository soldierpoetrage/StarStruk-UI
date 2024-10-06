from flask import Flask, render_template, request
import pandas as pd
from astroquery.gaia import Gaia

app = Flask(__name__)

# Load exoplanet data (ensure the CSV file path is correct)
df_exoplanets = pd.read_csv('exoplanets.csv')

@app.route('/')
def index():
    # Get all exoplanet names for the dropdown
    planet_names = df_exoplanets['pl_name'].tolist()
    return render_template('index.html', planet_names=planet_names)

# Function to fetch star data from Gaia DR3
def fetch_stars_for_exoplanet(ra, dec, radius=5):
    query = f"""
    SELECT TOP 1000 source_id, ra, dec, phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE CONTAINS(POINT('ICRS', ra, dec),
                   CIRCLE('ICRS', {ra}, {dec}, {radius}))=1
    """
    job = Gaia.launch_job(query)
    results = job.get_results()

    # Print results for debugging
    print(results)  # Print the entire results table
    print("Column names:", results.colnames)  # Print column names for confirmation

    # Convert to Pandas DataFrame for easier access
    stars_df = results.to_pandas()

    # Check if results are empty
    if stars_df.empty:
        print("No stars found.")
        return []

    # Ensure you're using the correct column names
    # Convert column names to lower case to avoid case sensitivity issues
    stars_df.columns = [col.lower() for col in stars_df.columns]

    # Extract data from results
    stars = []  # Initialize the list to store star data
    for index, row in stars_df.iterrows():
        stars.append({
            'source_id': row['source_id'],  # Access by the lowercase column name
            'ra': row['ra'],
            'dec': row['dec'],
            'phot_g_mean_mag': row['phot_g_mean_mag']
        })

    return stars


@app.route('/explore', methods=['POST'])
def explore():
    selected_planet = request.form.get('planet_select')

    if not selected_planet:
        return "No planet selected", 400  # Error handling for no selection

    # Get the selected planet's information
    exoplanet_info = df_exoplanets[df_exoplanets['pl_name'] == selected_planet].iloc[0]

    # Extract RA and Dec of the host star
    ra = exoplanet_info['ra']
    dec = exoplanet_info['dec']

    # Fetch nearby stars using Gaia DR3
    stars = fetch_stars_for_exoplanet(ra, dec)

    print(stars)

    # Since stars is already a list of dictionaries, you can use it directly
    return render_template('star_chart.html', stars=stars, planet=selected_planet)

if __name__ == '__main__':
    app.run(debug=True)
