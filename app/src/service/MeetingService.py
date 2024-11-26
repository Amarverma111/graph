from typing import Tuple

from contracts.meeting import MeetingResponse, GetMeetingResponse, DeleteMeetingResponse
from helper.httpclienthelper import HttpHelper, HttpStatusCode


class MeetingServices:
    def __init__(self, access_token, config):
        self.access_token = access_token
        self.config = config
        self.headers = {
            self.config['AUTHORIZATION_HEADER']: f"{self.config['BEARER_PREFIX']} {self.access_token}",
            self.config['CONTENT_TYPE_HEADER']: self.config['CONTENT_TYPE']
        }
        self.http_helper = HttpHelper(self.headers)

    async def get_meetings(self, GetMeetingRequest) -> Tuple[GetMeetingResponse, int]:
        start_date = GetMeetingRequest.start_date
        end_date = GetMeetingRequest.end_date

        if not all([start_date, end_date]):
            # Handle missing parameters case
            response_data = GetMeetingResponse(
                status="error",
                message="Missing required parameters",
                data=[]
            )
            return response_data,HttpStatusCode.NOT_FOUND.value  # Return error response with missing parameters

        """Fetch all meetings for the user."""
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/calendarView?startDateTime={start_date}Z&endDateTime={end_date}Z"
        response,status = await self.http_helper.get(url)
        if response.get("status") == "error":
            return GetMeetingResponse(
                status="error",
                message=response.get("message").get("message",""),
                data=[]
            ),status

        events =response.get('data', {}).get('value', [])
        get_detail = []
        # Loop through each event and insert its data into the get_details list
        for event in events:
            event_details = {
                "id": event.get("id"),
                "subject": event.get("subject"),
                "start_time": event.get("start", {}).get("dateTime"),
                "end_time": event.get("end", {}).get("dateTime"),
                "participants": [
                    attendee.get("emailAddress", {}).get("address")
                    for attendee in event.get("attendees", [])
                ]
            }
            get_detail.append(event_details)
        # Return successful response
        response_data = GetMeetingResponse(
            status="success",
            message=response.get("message").get("message",""),
            data=get_detail
        )
        return response_data ,status # Return the successful response with data


    async def create_meeting(self, CreateMeetingRequest) -> Tuple[MeetingResponse, int]:
        subject = CreateMeetingRequest.subject
        start_time = CreateMeetingRequest.start_time
        end_time = CreateMeetingRequest.end_time
        participants = CreateMeetingRequest.participants

        # Check for missing required parameters
        if not all([subject, start_time, end_time, participants]):
            response_data = MeetingResponse(
                status="error",
                message="Missing required parameters",
                data={}
            )
            return response_data,HttpStatusCode.NOT_FOUND.value  # Return error response with missing parameters

        # Construct the meeting data for the API request
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/events"
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

        # Send the POST request to create the meeting
        # response = requests.post(url, headers=self.headers, json=meeting_data)
        response_data,status = await self.http_helper.post(url, data=meeting_data)
        # import pdb;pdb.set_trace()
        if response_data.get("status") == "error":
            return MeetingResponse(
                status="error",
                message=response_data.get("message").get("message",""),
                data=dict()
            ),status

        return MeetingResponse(
            status="success",
            message="Meeting created successfully",
            data=response_data.get('data', {})

        ),status

    async def update_meeting(self, UpdateMeetingRequest) -> Tuple[MeetingResponse, int]:

        # Extract fields from the validated request
        meeting_id = UpdateMeetingRequest.meeting_id
        subject = UpdateMeetingRequest.subject
        start_time = UpdateMeetingRequest.start_time
        end_time = UpdateMeetingRequest.end_time
        participants = UpdateMeetingRequest.participants

        # Check for missing fields, but since Pydantic will already validate the required fields, this is optional
        if not all([meeting_id, subject, start_time, end_time, participants]):
            return MeetingResponse(
                status="error",
                message="Missing required parameters",
                data={}
            ),HttpStatusCode.NOT_FOUND.value

        """Update an existing meeting in the user's calendar."""
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"
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
        response_data,status = await self.http_helper.patch(url, data=updated_meeting_data)
        if response_data.get("status") == "error":
            return MeetingResponse(
                status="error",
                message=response_data.get("message").get("message",""),
                data=dict()
            ),status

        return MeetingResponse(
            status="success",
            message="Meeting created successfully",
            data=response_data.get('data', {})
        ),status


    async def delete_meeting(self, DeleteMeetingRequest) -> Tuple[DeleteMeetingResponse, int]:
        """Delete a meeting from the user's calendar."""
        meeting_request = DeleteMeetingRequest  # Get the validated request data

        meeting_id = meeting_request.meeting_id
        confirmation = meeting_request.confirm

        # Check for missing or invalid confirmation
        if confirmation != "yes":
            return DeleteMeetingResponse(
                status="error",
                message="Deletion not confirmed because of NO",
                data=[{"message": "Meeting deletion was not confirmed."}]  # Wrap in a list
            ),HttpStatusCode.NOT_FOUND.value

        # Construct the URL for deleting the meeting
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"

        # Send the DELETE request to remove the meeting
        response,status = await self.http_helper.delete(url)
        # Check for successful deletion (status code 204)
        if response.get("status") == "error":
            # Return success message when meeting is successfully deleted
            return DeleteMeetingResponse(
                status="error",
                message=response.get("message").get("message",""),
                data=[{}]
            ),status

        return DeleteMeetingResponse(
            status="success",
            message="Meeting deleted successfully",
            data=[response.get('data', {})]
        ),status

    async def reschedule_meeting(self, RescheduleMeetingRequest)-> Tuple[MeetingResponse, int]:

        # Extract fields from the validated request
        meeting_id = RescheduleMeetingRequest.meeting_id
        start_time = RescheduleMeetingRequest.start_time
        end_time = RescheduleMeetingRequest.end_time

        if not all([meeting_id, start_time, end_time]):
            return MeetingResponse(
                status="error",
                message="Missing required parameters",
                data={}
            ),HttpStatusCode.NOT_FOUND.value
        """Update an existing meeting in the user's calendar."""
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"
        updated_meeting_data_res = {
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
        }

        response,status = await self.http_helper.patch(url,data=updated_meeting_data_res)
        # import pdb;pdb.set_trace()
        if response.get("status") == "error":
            # Return success message when meeting is successfully deleted
            return MeetingResponse(
                status="error",
                message=response.get("message").get("message",""),
                data={}
            ),status

        return MeetingResponse(
            status="success",
            message="Meeting deleted successfully",
            data=response.get('data', {})
        ),status

    async def add_participate_update(self, AddParticipantsRequest)-> Tuple[MeetingResponse, int]:
        # Extract fields from the validated request
        meeting_id = AddParticipantsRequest.meeting_id
        subject = AddParticipantsRequest.subject
        participants = AddParticipantsRequest.participants

        # Check for missing fields, but since Pydantic will already validate the required fields, this is optional
        if not all([meeting_id, subject, participants]):
            return MeetingResponse(
                status="error",
                message="Missing required parameters",
                data={}
            ),HttpStatusCode.NOT_FOUND.value

        """Update an existing meeting in the user's calendar."""

        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/events/{meeting_id}"
        add_participate = {
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

        response,status = await self.http_helper.patch(url, data=add_participate)
        if response.get("status") == "error":
            # Return success message when meeting is successfully deleted
            return MeetingResponse(
                status="error",
                message=response.get("message").get("message",""),
                data={}
            ),status

        return MeetingResponse(
            status="success",
            message="Meeting deleted successfully",
            data=response.get('data', {})
        ),status
