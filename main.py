from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

app = Flask(__name__)

@app.route('/traffic-data', methods=['GET'])
def get_traffic_data():
    # Set up Selenium with a headless browser
    options = Options()
    options.headless = True  # To not open the browser window
    driver = webdriver.Chrome(options=options)

    # URL of the page
    url = "https://www.tomtom.com/traffic-index/ranking/"

    # Fetch the page content using Selenium
    driver.get(url)

    # Allow the page to load fully, increasing the wait time if necessary
    driver.implicitly_wait(30)  # Increase wait time for content to load

    # Get the page source after it has been fully loaded
    page_source = driver.page_source

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all script tags with the type application/json
    data = soup.find_all("script", {"type": "application/json"})

    driver.quit()  # Close the browser

    # Check if we got any script tags
    if data:
        try:
            # Parse the JSON data from the first script tag
            json_data = json.loads(data[0].string)

            # Print the structure of json_data for debugging
            print("Structure of json_data:", json_data)

            # Check if json_data is a dictionary or list, and handle it accordingly
            if isinstance(json_data, list):
                # Now, let's extract the information in an organized way
                city_data_list = []

                for city in json_data:  # Loop over each city data
                    city_data = {
                        "Name": city.get("name"),
                        "Key": city.get("key"),
                        "Country": city.get("country"),
                        "Country Code": city.get("countryCode"),
                        "Country Name": city.get("countryName"),
                        "Continent": city.get("continent"),
                        "Population": city.get("population"),
                        "Time Lost in Peak Hours": city.get("peakSummary", {}).get("timeLost"),
                        "Time Spent in Peak": city.get("peakSummary", {}).get("timeSpent"),
                        "Total Time in Peak": city.get("timeInPeaksPerYear"),
                        "Rank": city.get("rank"),
                        "Congestion Rank": city.get("rankCongestion"),
                    }
                    city_data_list.append(city_data)

                # Convert the data into a Pandas DataFrame for better structure and presentation
                df = pd.DataFrame(city_data_list)

                # Save the data to a CSV file on the desktop (Optional)
                desktop_path = "/Users/erivancouttolenc/Desktop/"
                csv_file_path = os.path.join(desktop_path, 'city_traffic_data.csv')
                df.to_csv(csv_file_path, index=False)

                return jsonify(city_data_list)  # Return JSON response of city traffic data

            else:
                return jsonify({"error": "Unexpected data format in JSON response", "json_structure": str(json_data)}), 500

        except json.JSONDecodeError as e:
            return jsonify({"error": "Error decoding JSON", "message": str(e)}), 500
    else:
        return jsonify({"error": "No data found in the page source"}), 404

if __name__ == '__main__':
    app.run(debug=True)
