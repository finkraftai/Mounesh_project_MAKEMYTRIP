from flask import Flask, request, jsonify
from datetime import datetime, timezone
from pymongo import MongoClient
from flask_cors import CORS
import http.client
import json
import ssl

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to convert date string to epoch timestamp
def date_to_epoch(date_string):
    return int(datetime.strptime(date_string, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())

# Function to generate timestamps for start and end dates
def generate_timestamps(start_date, end_date):
    start_epoch = date_to_epoch(start_date)
    end_epoch = date_to_epoch(end_date)
    return start_epoch * 1000, end_epoch * 1000

# Process data for ALL_DATA_HOTELS collection
def process_hotels_data(expense_client_id, external_org_id, start_date, end_date, Row_Labels, Org_name, Admin_Email_1):
    conn = http.client.HTTPSConnection("corpcb.makemytrip.com", context=ssl._create_unverified_context())
    payload = json.dumps({
        "expense-client-id": expense_client_id,
        "external-org-id": external_org_id,
        "to-date": end_date,
        "from-date": start_date,
        "report-type": "Hotel",
        "level": "INVOICE"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/csv',
        'Cookie': '_abck=17E55C4AA211B67E2013B8DAC748B665~-1~YAAQkqIauEhm0PiOAQAAQEXUKAu8ogNHA4YE+pyFZTq1saGrASWlhA8kfCC4GArQh9qL+GWi8MWlLzh0EUJfQHI2fS48tyAmml1lxxMPLZBNOeqOxumSf5tATsnBNKiSe0ZLb2yhR5KO7GodyQKdIKLOc27kopr/uaoGQaDXEVFD7UJ1Bt7eMtdvCcTakoWAxar8wt/Bcj956TRGUV0fCR9t0C7WcVZJtqhDyzP6APUXeMM2EPRx60TJnG4ba1pmSy+qrh6T+rFttggeI+ax1RSCGkktS/+M+/xrH2ON5GE280uyRrGaxmWeC166wRKmUci2zShIj9vqC+pX7Y4GxwB9Ya4fGA+fnASuvNYI/Y8lsbzkMKmEdev6PUgkaoDz49aF02oiYxT9NfQ=~-1~-1~-1; bm_sz=EE2FF900A19306A96FC662DCC6836545~YAAQkqIauElm0PiOAQAAQEXUKBeK15jMKLyYOrEBBX47YN9HQqOryl7vA5CUaKROE/aK3o5iE4JaSlnnPYSTdGUEVTyVlDD38NqOhQ75uQqveRHy/kRqY3Bfdsg/M+U/8isJaj9s9Z7zyh8pFx1J4z8C5wmD2WCvfHe608W6+rBoLYrNQIDtoZ/SHc55JERT/aG0kO0JvX3quUCoKPLcblbvwkJZ+jqTEY73DgGUsph8EYJqocMujyZKRM6POUBi3s8cSZ6fbTtQWadSW5T0wJKcIJmsPfFcKdnfFLIDx7HFav4wA9Q4jkxdtuaCfAaHDGA2HIRv5O58N+s5+Fbu7TbG64Bopr663nYyD0TPRucssg==~4473396~3556929'
    }
    conn.request("POST", "/transaction/data", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    csv_lines = data.split('\n')
    headers = csv_lines[0].split(',')
    csv_data = []

    for line in csv_lines[1:]:
        values = line.split(',')
        csv_data.append(dict(zip(headers, values)))

    additional_data = {
        "Row_Labels": Row_Labels,
        "Org_name": Org_name,
        "Admin_Email_1": Admin_Email_1
    }

    for entry in csv_data:
        entry.update(additional_data)

    save_to_mongodb(csv_data, "MakeMyTrip", "Mounesh")

# Process data for other collections
def process_other_data(expense_client_id, external_org_id, start_date, end_date, Row_Labels, Org_name, Admin_Email_1, collection_name):
    conn = http.client.HTTPSConnection("example.com", context=ssl._create_unverified_context())
    payload = json.dumps({
        "expense-client-id": expense_client_id,
        "external-org-id": external_org_id,
        "to-date": end_date,
        "from-date": start_date,
        "report-type": "FLIGHT",
        "level": "INVOICE"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/csv',
        'Cookie': '_abck=17E55C4AA211B67E2013B8DAC748B665~-1~YAAQmKIauIuvyfGOAQAAABH7CgvADy+xDRdL180XIaiJ3irmnnBSM+RMIwv5tkxrggRXsYaCFbxY8x1MmaHVyogQy3PgqByI6VhzRrVFc/CO6bVpvvz9eEUnu8HSpJ2/6IEYcO3szuvfu5Rie/3l2ncHljNPodObiY/v/O5T1L6DqjHiprPE1XAYxMO4bcbWFY5bdHd/5lt7o1M4NYxPdDAHZ0AzgxBokaEPlKqNUOwcrdbz9yGBdKpEuWqQ5dL3kSNQUmdkJMCrR1zj9yEaMd+q1E+fJxS18J/IDquf26vlOcrbY7Rn7z8wBcwvuAOh9tBW2875OypRY9Q1tChLDA7UHw95ggCJ/6H2XxBEZI3Pn3UVyUGJWfS1j2lveih5mWezKAiexsctMR4=~-1~-1~-1; bm_sz=6D14478164410E7C7B7A8B4A2D9159E5~YAAQmKIauIyvyfGOAQAAABH7ChcmVrqMEgi4J1TS4LA7oDvhVP8acrCwLRC2SY+zqfIL77pjl+JBfZ1Wn3aTPAY11YY6bSNry88ixL90LlqPK+zc368emSSnH0Wc7iRnNAY8x5nf6IUQJTZipbluHJX/P9sbHZB8evG8cw5SvdZiKYrmS0xkQYJCnbPqXSLt3t1HvZ3THrjYXWTEM/P24SMfVgv2kq0KXuwXSaOAQJ1sd++QQeymTa3NpcWSzI9K25/CA2uQWzGN5aqm0q/ad/Q1sl+iKweDTJUhQzvBDRi/DPenESz12FUo87xaR2Ds+Mh61y6JUyT8bDm/qb6LVWib0jet886lQz96mTY8TE71~3486008~3556163'    
    }
    conn.request("POST", "/transaction/data", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    csv_lines = data.split('\n')
    headers = csv_lines[0].split(',')
    csv_data = []

    for line in csv_lines[1:]:
        values = line.split(',')
        if len(values) == len(headers):
            row = {}
            for i, header in enumerate(headers):
                row[header] = values[i]
            csv_data.append(row)

    additional_data = {
        "Row_Labels": Row_Labels,
        "Org_name": Org_name,
        "Admin_Email_1": Admin_Email_1
    }

    for entry in csv_data:
        entry.update(additional_data)

    save_to_mongodb(csv_data, "MakeMyTrip", collection_name)

# Save data to MongoDB
def save_to_mongodb(data, db_name, collection_name):
    url = 'mongodb://airlinedb_user:8649OV57IGR3Y1JS@ec2-43-205-133-199.ap-south-1.compute.amazonaws.com/admin?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.3'
    client = MongoClient(url, maxIdleTimeMS=None)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(data)
    # print(data)

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    expense_client_id = data.get('expense-client-id')
    external_org_id = data.get('external-org-id')
    collection_name = data.get('collection_name')

    Row_Labels = data.get('Row_Labels')
    Org_name = data.get('Org_name')
    Admin_Email_1 = data.get('Admin_Email_1')
    start_date, end_date = generate_timestamps(start_date, end_date)
    
    try:
        if collection_name == "Mounesh":
            process_hotels_data(expense_client_id, external_org_id, start_date, end_date, Row_Labels, Org_name, Admin_Email_1)
        else:
            process_other_data(expense_client_id, external_org_id, start_date, end_date, Row_Labels, Org_name, Admin_Email_1, collection_name)

        return jsonify({'message': 'Data saved successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)






















