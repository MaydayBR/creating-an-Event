from flask import Flask, render_template, request, redirect, flash
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Eventbrite API credentials
EVENTBRITE_TOKEN = os.getenv('EVENTBRITE_TOKEN')
ORGANIZATION_ID = 'YOUR_ORGANIZATION_ID'

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

    try:
        # Make the request to Eventbrite API
        response = requests.post(
            f'https://www.eventbriteapi.com/v3/organizations/{ORGANIZATION_ID}/events/',
            headers=headers,
            data=json.dumps(event_data)
        )
        response.raise_for_status()

        flash('Event created successfully!', 'success')

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        flash(f"Error creating event: {response.json().get('error_description', 'Unknown error')}", 'error')

    except Exception as err:
        print(f"Other error occurred: {err}")
        flash(f"An error occurred: {err}", 'error')

    return redirect('/')

# Route to list events by venue
@app.route('/venue/<venue_id>/events', methods=['GET'])
def list_events_by_venue(venue_id):
    try:
        # Headers for the request
        headers = {
            'Authorization': f'Bearer {EVENTBRITE_TOKEN}',
        }

        # Make the GET request to list events at the venue
        response = requests.get(
            f'https://www.eventbriteapi.com/v3/venues/{venue_id}/events/',
            headers=headers
        )

        # Check if the request was successful
        response.raise_for_status()
        events_info = response.json()

        return render_template('events_list.html', events=events_info['events'])

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        flash(f"Error retrieving events: {http_err}", 'error')
        return redirect('/')

    except Exception as err:
        print(f"Other error occurred: {err}")
        flash(f"An error occurred: {err}", 'error')
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
