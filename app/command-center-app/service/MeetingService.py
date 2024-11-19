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
        response = requests.post(url, headers=self.headers, json=meeting_data)
        response.raise_for_status()
        return response.json()

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

        response = requests.patch(url, headers=self.headers, json=updated_meeting_data)
        response.raise_for_status()
        return response.json()

    async def get_meetings(self, config, start_date,end_date):
        """Fetch all meetings for the user."""
        # url = f"{config['GRAPH_API_ENDPOINT']}/me/events?$filter=start/dateTime ge '{start_date}' and end/dateTime le '{end_date}'"
        url =f"{config['GRAPH_API_ENDPOINT']}/me/calendarView?startDateTime={start_date}T00:00:00Z&endDateTime={end_date}T23:59:59Z "
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        events = response.json().get("value", [])

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

        response = requests.patch(url, headers=self.headers, json=updated_meeting_data_res)
        response.raise_for_status()
        return response.json()


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
        response = requests.patch(url, headers=self.headers, json=updated_meeting_data)
        response.raise_for_status()
        return response.json()
