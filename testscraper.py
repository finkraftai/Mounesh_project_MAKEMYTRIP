import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Function to convert date string to epoch timestamp
def date_to_epoch(date_string):
    try:
        return int(datetime.strptime(date_string, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        logging.error(f"Invalid date format for date string: {date_string}")
        raise ValueError("Invalid date format")

# Function to generate timestamps for start and end dates
def generate_timestamps(start_date, end_date):
    try:
        start_epoch = date_to_epoch(start_date)
        end_epoch = date_to_epoch(end_date)
        return start_epoch * 1000, end_epoch * 1000
    except ValueError as e:
        logging.error(f"Error generating timestamps: {str(e)}")
        raise ValueError(str(e))

# API endpoint to handle POST requests from the frontend
@app.route('/api/data', methods=['POST'])
def handle_post_request():
    try:
        # Get the JSON data from the POST request
        data = request.json

        # Extract values from the JSON data
        start_date_input = data.get('start_date')
        end_date_input = data.get('end_date')
        expense_client_id = data.get('expense-client-id')
        external_org_id = data.get('external-org-id')
        collection_name = data.get('collection_name')

        # Generate timestamps for the start and end dates
        from_date, to_date = generate_timestamps(start_date_input, end_date_input)

        # Placeholder for your API request and MongoDB code here...
        # Simulate processing time
        import time
        time.sleep(1)  # Simulate 1 second processing time

        # Log success message
        logging.info('Request processed successfully.')

        # Prepare and return the response to the frontend
        response_data = {
            'status': 'success',
            'message': 'Data received and processed successfully',
            'data': {}  # Add your response data here if needed
        }
        return jsonify(response_data)

    except ValueError as e:
        logging.error(f"ValueError occurred: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400  # Bad Request

    except Exception as e:
        # Log the exception
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
