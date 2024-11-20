import requests

class MeetingServices:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def create_meeting(self, subject, start_time, end_time, participants, config):
        """Create a new meeting in the user's calendar."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/events"
        meeting_data = {
            "subject": subject,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
            "attendees": [
                {
                    "emailAddress": {
                        "address": email,
                        "name": name
                    },
                    "type": "required"
                } for name, email in participants
            ]
        }
    try:
        response = requests.post(url, headers=self.headers, json=meeting_data)
        response.raise_for_status()  # Raise an error for non-200 status codes
        return response.json()  # Process the successful response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
        # Additional handling based on status code
        if response.status_code == 400:
            print("Bad Request: Check the meeting_data payload.")
        elif response.status_code == 401:
            print("Unauthorized: Check your API key or authentication headers.")
        elif response.status_code == 500:
            print("Server error: Try again later or contact support.")
        else:
            print("An unexpected error occurred.")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None

    async def update_meeting(self, meeting_id, subject, start_time, end_time, participants, config):
        """Update an existing meeting in the user's calendar."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"
        updated_meeting_data = {
            "subject": subject,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
            "attendees": [
                {
                    "emailAddress": {
                        "address": email,
                        "name": name
                    },
                    "type": "required"
                } for name, email in participants
            ]
        }
    try:
        response = requests.patch(url, headers=self.headers, json=updated_meeting_data)
        response.raise_for_status()  # Raise an error for non-200 status codes
        return response.json()  # Process the successful response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
        # Additional handling based on status code
        if response.status_code == 400:
            print("Bad Request: Check the meeting_data payload.")
        elif response.status_code == 401:
            print("Unauthorized: Check your API key or authentication headers.")
        elif response.status_code == 500:
            print("Server error: Try again later or contact support.")
        else:
            print("An unexpected error occurred.")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None

    async def get_meetings(self, config, start_date,end_date):
        """Fetch all meetings for the user."""
        # url = f"{config['GRAPH_API_ENDPOINT']}/me/events?$filter=start/dateTime ge '{start_date}' and end/dateTime le '{end_date}'"
        url =f"{config['GRAPH_API_ENDPOINT']}/me/calendarView?startDateTime={start_date}T00:00:00Z&endDateTime={end_date}T23:59:59Z "
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch events. Status code: {response.status_code}")
            print(f"Error details: {response.text}")
            return []  # Return an empty list or handle as needed
        response.raise_for_status()
        try:
            events = response.json().get("value", [])
            if not isinstance(events, list):  # Ensure events is a list
                logging.error("Unexpected API response format.")
                return []
        except ValueError:
            logging.error("Failed to parse JSON response.")
            return []

        return [
            {
                "id": event.get("id"),
                "subject": event.get("subject"),
                "start_time": event.get("start", {}).get("dateTime"),
                "end_time": event.get("end", {}).get("dateTime"),
                "participants": [
                    attendee.get("emailAddress", {}).get("address")
                    for attendee in event.get("attendees", [])
                ]
            }
            for event in events
        ]

    async def delete_meeting(self, meeting_id, config):
        """Delete a meeting from the user's calendar."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            return {"message": "Meeting deleted successfully"}
        else:
            response.raise_for_status()

    async def reschedul_meeting(self, meeting_id, subject, start_time, end_time, participants, config):
        """Update an existing meeting in the user's calendar."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"
        updated_meeting_data_res = {
            "subject": subject,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
        }
        try:
            response = requests.patch(url, headers=self.headers, json=updated_meeting_data_res)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
            # Additional handling based on status code
            if response.status_code == 400:
                print("Bad Request: Check the meeting_data payload.")
            elif response.status_code == 401:
                print("Unauthorized: Check your API key or authentication headers.")
            elif response.status_code == 500:
                print("Server error: Try again later or contact support.")
            else:
                print("An unexpected error occurred.")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            return None


    async def add_participate_update(self, meeting_id, subject, participants, config):
        """Update an existing meeting in the user's calendar."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"
        updated_meeting_data = {
            "subject": subject,
            "attendees": [
                {
                    "emailAddress": {
                        "address": email,
                        "name": name
                    },
                    "type": "required"
                } for name, email in participants
            ]
        }
        try:
            response = requests.patch(url, headers=self.headers, json=updated_meeting_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
            # Additional handling based on status code
            if response.status_code == 400:
                print("Bad Request: Check the meeting_data payload.")
            elif response.status_code == 401:
                print("Unauthorized: Check your API key or authentication headers.")
            elif response.status_code == 500:
                print("Server error: Try again later or contact support.")
            else:
                print("An unexpected error occurred.")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            return None
