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
    
    # Connect to the external API and fetch the CSV data
    if collection_name == "PUNIT_HOTEL":
        try:
            conn = http.client.HTTPSConnection("corpcb.makemytrip.com", context=ssl._create_unverified_context())
            payload = json.dumps({
                "expense-client-id": expense_client_id,
                "external-org-id": external_org_id,
                "to-date": end_date,  # Assuming end_date is in milliseconds since epoch
                "from-date": start_date,  # Assuming start_date is in milliseconds since epoch
                "report-type":"Hotel",
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
            print(data)
            # Assuming 'final' is a CSV string, you can split it into lines
            csv_lines = data.split('\n')
            # Assuming the first row contains column headers
            headers = csv_lines[0].split(',')
            # Initialize an empty list to store the dictionaries
            csv_data = []
            # Iterate over the remaining rows and create dictionaries
            for line in csv_lines[1:]:
                values = line.split(',')
                csv_data.append(dict(zip(headers, values)))
            additional_data = {
                    "Row_Labels": Row_Labels,
                    "Org_name": Org_name,
                    "Admin_Email_1": Admin_Email_1
                }
            print("csv data",str(csv_data))
            print("type ",type(csv_data[0]))
            temp=[]
            for row in csv_data:
                row.update(additional_data)
                temp.append(row)
            csv_data=temp
            # print(csv_data)
            # Input collection name from the user
            # collection_name = input("Enter collection name: ")
            url = 'mongodb://airlinedb_user:8649OV57IGR3Y1JS@ec2-43-205-133-199.ap-south-1.compute.amazonaws.com/admin?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.3'
            client = MongoClient(url, maxIdleTimeMS=None)
            print("MongoDB connection is successful.")
            # Connect to MongoDB
            db = client['MakeMyTrip']
            # Create or access the collection based on user input
            collection = db[collection_name]
            # Insert data into MongoDB
            try:
                collection.insert_many(csv_data)
                print("Data inserted successfully.")
            except Exception as e:
                print("An error occurred while inserting data:", e)
            print("Data saved to MongoDB")
            return jsonify({'message': 'Data saved successfully.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        try:
            conn = http.client.HTTPSConnection("corpcb.makemytrip.com", context=ssl._create_unverified_context())
            payload = json.dumps({
                "expense-client-id": expense_client_id,
                "external-org-id": external_org_id,
                "to-date": end_date,  # Assuming end_date is in milliseconds since epoch
                "from-date": start_date,  # Assuming start_date is in milliseconds since epoch
                "report-type": "FLIGHT",
                "level": "INVOICE"
            })
            # print(payload)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'text/csv',
                'Cookie': '_abck=17E55C4AA211B67E2013B8DAC748B665~-1~YAAQmKIauIuvyfGOAQAAABH7CgvADy+xDRdL180XIaiJ3irmnnBSM+RMIwv5tkxrggRXsYaCFbxY8x1MmaHVyogQy3PgqByI6VhzRrVFc/CO6bVpvvz9eEUnu8HSpJ2/6IEYcO3szuvfu5Rie/3l2ncHljNPodObiY/v/O5T1L6DqjHiprPE1XAYxMO4bcbWFY5bdHd/5lt7o1M4NYxPdDAHZ0AzgxBokaEPlKqNUOwcrdbz9yGBdKpEuWqQ5dL3kSNQUmdkJMCrR1zj9yEaMd+q1E+fJxS18J/IDquf26vlOcrbY7Rn7z8wBcwvuAOh9tBW2875OypRY9Q1tChLDA7UHw95ggCJ/6H2XxBEZI3Pn3UVyUGJWfS1j2lveih5mWezKAiexsctMR4=~-1~-1~-1; bm_sz=6D14478164410E7C7B7A8B4A2D9159E5~YAAQmKIauIyvyfGOAQAAABH7ChcmVrqMEgi4J1TS4LA7oDvhVP8acrCwLRC2SY+zqfIL77pjl+JBfZ1Wn3aTPAY11YY6bSNry88ixL90LlqPK+zc368emSSnH0Wc7iRnNAY8x5nf6IUQJTZipbluHJX/P9sbHZB8evG8cw5SvdZiKYrmS0xkQYJCnbPqXSLt3t1HvZ3THrjYXWTEM/P24SMfVgv2kq0KXuwXSaOAQJ1sd++QQeymTa3NpcWSzI9K25/CA2uQWzGN5aqm0q/ad/Q1sl+iKweDTJUhQzvBDRi/DPenESz12FUo87xaR2Ds+Mh61y6JUyT8bDm/qb6LVWib0jet886lQz96mTY8TE71~3486008~3556163'
            }
            # print(headers)

            
            conn.request("POST", "/transaction/data", payload, headers)
            res = conn.getresponse()
            # print(res)
            data = res.read()
            final= data.decode("utf-8")
                # print("data recived---------- ",final)
        

                # Assuming 'final' is a CSV string, you can split it into lines
            csv_lines = final.split('\n')

                # Assuming the first row contains column headers
            headers = csv_lines[0].split(',')

            # Initialize an empty list to store the dictionaries
            csv_data = []

                # Iterate over the remaining rows and create dictionaries
            for line in csv_lines[1:]:
                values = line.split(',')
                if len(values) == len(headers):
                    row = {}
                    for i, header in enumerate(headers):
                        row[header] = values[i]
                    csv_data.append(row)

                # Convert the list of dictionaries to JSON
            json_data = csv_data

                
                # Include additional data in each dictionary in csv_data
            additional_data = {
                    "Row_Labels": Row_Labels,
                    "Org_name": Org_name,
                    "Admin_Email_1": Admin_Email_1
                }
                # print("csv data",str(csv_data))
                # print("type ",type(csv_data[0]))
            temp=[]
            for row in json_data:
                row.update(additional_data)
                temp.append(row)
            json_data=temp
            # print(json_data)
                # for row in csv_data:
                #     row.update(additional_data)
                # csv_data.ap`pend(dict(zip(additional_data)))
                
                # Connect to MongoDB
            url = 'mongodb://airlinedb_user:8649OV57IGR3Y1JS@ec2-43-205-133-199.ap-south-1.compute.amazonaws.com/admin?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.3'
            client = MongoClient(url, maxIdleTimeMS=None)
            print("MongoDB connection is successful.")
            db = client['MakeMyTrip']
                # Create or access the collection based on user input
            collection = db[collection_name]
                    # Insert data into MongoDB
            # print(csv_data)
            try:
                # Uncomment the line below to insert data into MongoDB
                collection.insert_many(json_data)
                print("Data inserted successfully.")
                return jsonify({'message': 'Data saved successfully.'}), 200
            except Exception as e:
                print("An error occurred while inserting data:", e)
                return jsonify({'error': 'Error occurred while inserting data into MongoDB.'}), 500
        except Exception as e:
            print("An error occurred during API request:", e)
            return jsonify({'error': 'Error occurred during API request.'+str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)












