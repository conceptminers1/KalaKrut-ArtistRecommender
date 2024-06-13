import pandas as pd
from flask import Flask, render_template, request

# Load data from CSV
data = pd.read_csv("artists.csv", index_col=0)

# Define function to filter artists based on user selection
def recommend_artists(genre, subgenre, location, min_discography, min_deals):
    # Convert 'Discography (Count)' and 'Deals Completed' to integers, handling missing values
    data["Discography (Count)"] = pd.to_numeric(
        data["Discography (Count)"].replace("", 0), errors="coerce"
    )  # Fill empty strings with 0, coerce other errors
    data["Deals Completed"] = pd.to_numeric(
        data["Deals Completed"].replace("", 0), errors="coerce"
    )

    # Option 1: Using pd.isnull() and filling missing values (if desired)
    # Check for missing values in relevant columns and potentially fill them
    if pd.isnull(data["Discography (Count)"]).any():
        # Fill missing values with median (or another strategy)
        data["Discography (Count)"] = data["Discography (Count)"].fillna(data["Discography (Count)"].median())
    if pd.isnull(data["Deals Completed"]).any():
        # Fill missing values with 0 (or another strategy)
        data["Deals Completed"] = data["Deals Completed"].fillna(0)

    # Option 2: Using pd.isna() for filtering (alternative to missing value handling)
    # Filter out rows with missing values (assuming missing values indicate incomplete data)
    filtered_data = data[
        ~pd.isna(data["Discography (Count)"])
        & ~pd.isna(data["Deals Completed"])
        & (data["Genre"] == genre)
        & (data["Subgenres"].str.contains(subgenre))
        & (data["Location"] == location)
        & (data["Discography (Count)"] >= min_discography)
        & (data["Deals Completed"] >= min_deals)
    ]

    # Check if there are enough recommendations
    if len(filtered_data) < 5:
        # Not enough artists found
        recommendations = [(row['Name'], row['Email']) for row in filtered_data.sample(len(filtered_data)).to_dict('records')] 
        return recommendations, "Not enough artists matched your criteria. Try broadening your search."
    else:
        # Randomly select 5 artists
        recommendations = [(row['Name'], row['Email']) for row in filtered_data.sample(5).to_dict('records')]
        return recommendations, None  # No additional message

app = Flask(__name__)

@app.route("/")
def index():
    genres = data["Genre"].unique()
    locations = data["Location"].unique()
    return render_template("index.html", genres=genres, locations=locations)

@app.route("/recommend", methods=["POST"])
def recommend():
    genre = request.form.get("genre")
    subgenre = request.form.get("subgenre")
    location = request.form.get("location")
    min_discography = request.form.get("min_discography", type=int) 
    min_deals = request.form.get("min_deals", type=int) 

    recommendations, message = recommend_artists(
        genre, subgenre, location, min_discography, min_deals
    )

    return render_template("recommendations.html", recommendations=recommendations, message=message)

if __name__ == "__main__":
    app.run(debug=True)