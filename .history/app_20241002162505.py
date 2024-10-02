from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import pytz

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key securely
csrf = CSRFProtect(app)

# Eventbrite API credentials
EVENTBRITE_TOKEN = os.getenv('EVENTBRITE_TOKEN')
ORGANIZATION_ID = os.getenv('ORGANIZATION_ID')

if not EVENTBRITE_TOKEN or not ORGANIZATION_ID:
    raise ValueError("Eventbrite token and Organization ID must be set in environment variables.")

# Flask-WTF Form
class EventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_description = TextAreaField('Event Description', validators=[DataRequired()])
    event_date = DateField('Event Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    event_start_time = TimeField('Event Start Time (HH:MM)', format='%H:%M', validators=[DataRequired()])
    event_end_time = TimeField('Event End Time (HH:MM)', format='%H:%M', validators=[DataRequired()])

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    form = EventForm()
    if form.validate_on_submit():
        # Process the form data
        event_name = form.event_name.data
        event_description = form.event_description.data
        event_date = form.event_date.data
        event_start_time = form.event_start_time.data
        event_end_time = form.event_end_time.data

        # Combine date and time
        local_timezone = pytz.timezone('America/New_York')
        local_start_datetime = local_timezone.localize(datetime.combine(event_date, event_start_time))
        local_end_datetime = local_timezone.localize(datetime.combine(event_date, event_end_time))

        # Convert to UTC
        event_utc_start_time = local_start_datetime.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        event_utc_end_time = local_end_datetime.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        event_local_start_time = local_start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        event_local_end_time = local_end_datetime.strftime('%Y-%m-%dT%H:%M:%S')

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
                    "utc": event_utc_start_time,
                    "local": event_local_start_time
                },
                "end": {
                    "timezone": "America/New_York",
                    "utc": event_utc_end_time,
                    "local": event_local_end_time
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
            return redirect('/')

        except requests.exceptions.HTTPError as http_err:
            error_message = response.json().get('error_description', str(http_err))
            print(f"HTTP error occurred: {http_err}")
            flash(f"Error creating event: {error_message}", 'error')
            return redirect('/')

        except Exception as err:
            print(f"Other error occurred: {err}")
            flash(f"An error occurred: {err}", 'error')
            return redirect('/')

    return render_template('create_event.html', form=form)

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

        return render_template('events_list.html', events=events_info.get('events', []))

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
