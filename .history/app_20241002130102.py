from flask import Flask, render_template, request, redirect, flash
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Eventbrite API credentials
EVENTBRITE_TOKEN = '2AMSUVKWV5T2GIUVMMJV'  # Private token
ORGANIZATION_ID = 'YOUR_ORGANIZATION_ID'  # Replace this with your actual organization ID

# Route for the home page
@app.route('/')
def home():
    return render_template('create_event.html')

# Route to handle event creation
@app.route('/create_event', methods=['POST'])
def create_event():
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
            "is_free": True,
            "locale": "en_US"
        }
    }

    # Headers for the request
    headers = {
        'Authorization': f'Bearer {EVENTBRITE_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Make the request to Eventbrite API
    try:
        response = requests.post(
            f'https://www.eventbriteapi.com/v3/organizations/{ORGANIZATION_ID}/events/',
            headers=headers,
            data=json.dumps(event_data)
        )
        response.raise_for_status()  # Raises HTTPError if the response was unsuccessful
        flash('Event created successfully!', 'success')
    except requests.exceptions.HTTPError as http_err:
        flash(f"HTTP error occurred: {http_err}", 'error')
    except Exception as err:
        flash(f"Error creating event: {err}", 'error')
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
