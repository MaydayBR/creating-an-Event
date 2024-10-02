from flask import Flask, render_template, request, redirect, flash
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Eventbrite API credentials
EVENTBRITE_TOKEN = '2AMSUVKWV5T2GIUVMMJV'
ORGANIZATION_ID = 'YOUR_ORGANIZATION_ID'

# Route for the home page
@app.route('/')
def home():
    return render_template('create_event.html')

# Route to retrieve organization ID and event creation
@app.route('/create_event', methods=['POST'])
def create_event():
    try:
        # Step to retrieve organization details
        headers = {
            'Authorization': f'Bearer {EVENTBRITE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        org_response = requests.get('https://www.eventbriteapi.com/v3/users/me/organizations/', headers=headers)
        
        if org_response.status_code == 200:
            org_data = org_response.json()
            print("Organization Info:", json.dumps(org_data, indent=4))
            # Get the organization ID from the first organization
            organization_id = org_data['organizations'][0]['id']
        else:
            flash(f"Error retrieving organization info: {org_response.json().get('error_description', 'Unknown error')}", 'error')
            return redirect('/')
        
        # Event data collection
        event_name = request.form['event_name']
        event_description = request.form['event_description']
        event_time = request.form['event_time']  # Time will be in HH:MM format

        # Convert event time to UTC for Eventbrite API (example: 11:00 AM -> 15:00 UTC)
        event_utc_time = f"2024-10-10T{event_time}:00Z"

        # Eventbrite API request data
        event_data = {
            "event": {
                "name": {
                    "html": event_name
                },
                "description": {
                    "html": event_description
                },
                "start": {
                    "timezone": "America/New_York",
                    "utc": event_utc_time
                },
                "end": {
                    "timezone": "America/New_York",
                    "utc": event_utc_time  # You can adjust this for event end time
                },
                "currency": "USD",
                "online_event": False,
                "listed": True,
                "shareable": True,
                "invite_only": False,
                "show_remaining": True,
                "capacity": 100,
                "locale": "en_US"
            }
        }

        # Headers for the request
        headers = {
            'Authorization': f'Bearer {EVENTBRITE_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Make the request to Eventbrite API
        response = requests.post(
            f'https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/',
            headers=headers,
            data=json.dumps(event_data)
        )

        # Check if the request was successful
        if response.status_code == 200:
            flash('Event created successfully!', 'success')
        else:
            flash(f"Error creating event: {response.json().get('error_description', 'Unknown error')}", 'error')

    except requests.exceptions.RequestException as e:
        print(f"HTTP error occurred: {e}")
        flash(f"HTTP error occurred: {str(e)}", 'error')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
