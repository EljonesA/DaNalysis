# DaNalysis Flask Application

This Flask application provides a web interface for viewing various macroeconomic data visualizations, including nominal GDP, population trends, GDP per capita, exchange rates, and inflation rates. Users can log in, sign up, and view different dashboards showcasing this data in interactive charts.

## Features

- **User Authentication:** 
  - Users can sign up, log in, and log out.
  - Access to the dashboards is restricted to authenticated users.

- **Dashboards:**
  - **Dashboard 1:** Displays historical nominal GDP, population trends, and GDP per capita data.
  - **Dashboard 2:** Shows USD/KES exchange rates from 2019 to date.
  - **Dashboard 3:** Contains two pages:
    - **Page 1:** Freely accessible, comparing the current month's inflation with the prior month's.
    - **Page 2:** Locked, showing historical monthly inflation trends in Kenya.

- **Data Filters:**
  - Charts are customizable using filters that adjust the time period (e.g., 5Y, 10Y, Full dataset).
  
## Routes

### User Authentication

- **/login:** Login page for users.
- **/signup:** Signup page for new users.
- **/logout:** Logs out the user and redirects to the login page.

### Dashboards

- **/dashboard1:** Displays nominal GDP, population, and GDP per capita trends.
- **/dashboard2:** Displays USD/KES exchange rates.
- **/dashboard3:** Displays inflation trends, with restricted access for historical data.

### Data Fetching Routes

- **/fetch_filtered_data:** Fetches filtered data for GDP, population, or GDP per capita based on the selected period.
- **/fetch_filtered_exchanges:** Fetches filtered data for USD/KES exchange rates based on the selected period.
- **/fetch_filtered_inflation:** Fetches filtered data for inflation rates based on the selected period.
- **/fetch_filtered_shares:** Fetches filtered data for share prices based on the selected period.
- **/fetch_filtered_shares_more:** Fetches additional filtered data for share prices for a different dataset.

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip (Python package installer)
- Flask

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository

2. Clone the repository:

   ```bash
   pip install -r requirements.txt

3. Run the application:

   ```bash
   python app.py or flask run

4. Access the application in your browser at:

   ```bash
   http://127.0.0.1:5000/

## Dependencies
- Flask: Web framework for Python.
- pyrebase: Python wrapper for Firebase API.
- pandas: Data manipulation and analysis library.
- plotly: Library for creating interactive charts and plots.

## License
- This project is licensed under the MIT License - see the LICENSE file for details.

### Contact
- For any inquiries or issues, please contact [user@gmail.com].