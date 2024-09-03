import requests
from tabulate import tabulate  # Install tabulate: pip install tabulate

# Define the API endpoint URL
url = "https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=533096&flag=0&fromdate=&todate=&seriesid="

# Other APIs
## BSE
url1 = "https://api.bseindia.com/BseIndiaAPI/api/HighLow/w?Type=EQ&flag=C&scripcode=500209"
url2 = "https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=533096&flag=0&fromdate=&todate=&seriesid="
url3 = "https://api.bseindia.com/BseIndiaAPI/api/EQPeerGp/w?scripcode=533096&scripcomare="
url4 = "https://api.bseindia.com/BseIndiaAPI/api/ComHeadernew/w?quotetype=EQ&scripcode=533096&seriesid="
url5 = "https://api.bseindia.com/BseIndiaAPI/api/HighLow/w?Type=EQ&flag=C&scripcode=533096"
url6 = "https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=533096&flag=0&fromdate=&todate=&seriesid="

## NSE
url7 = "https://www.nseindia.com/api/quote-equity?symbol=AXISBANK"

# Set headers (optional, but recommended to match curl behavior)
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.bseindia.com",
    "referer": "https://www.bseindia.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# Send the GET request and handle potential errors
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for non-200 status codes
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
    exit(1)

# Extract data from the JSON response
data = response.json()

print(f'Reponse Date : {data}')

# # Check if data is empty or has an error message
# if not data or "error" in data:
#     print("Error fetching data:", data.get("error", "No data found"))
#     exit(1)
#
# # Extract relevant information for the table
# table_data = []
# table_data.append([
#     data["Fifty2WkHigh_adj"],
#     data["Fifty2WkHigh_adjDt"],
#     data["Fifty2WkLow_adj"],
#     data["Fifty2WkLow_adjDt"],
#     data["MonthHighLow"],
#     data["WeekHighLow"]
# ])
#
# # Create and display the table
# table_headers = [
#     "52-Week High (Adj)",
#     "52-Week High (Adj) Date",
#     "52-Week Low (Adj)",
#     "52-Week Low (Adj) Date",
#     "Month High/Low",
#     "Week High/Low"
# ]
# print(tabulate(table_data, headers=table_headers))