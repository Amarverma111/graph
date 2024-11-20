import requests
import base64
from quart import (Blueprint, Quart, request, jsonify)
from service.MeetingService import MeetingServices
from service.load_config_yaml import load_config
from service.EmailService import EmailServices
from service.TaskService import  TaskServices
from contracts.meeting import CreateMeetingRequest, MeetingResponse, DeleteMeetingRequest, UpdateMeetingRequest, RescheduleMeetingRequest,\
    AddParticipantsRequest, error_response, success_response, GetMeetingResponse, GetMeetingRequest
from contracts.email import CreateEmailRequest, DeleteEmailRequest, SendEmailRequest, ForwardEmailRequest, ReplyEmailRequest, MessageSentResponse, GetEmailRequest
from contracts.task import TaskResponse, TaskCreateHeadingRequest, TaskCreateSubRequest, TaskCreateResponse
from pydantic import ValidationError
from data_source.Graph_api import MSFTGraph
from urllib.parse import urlencode


# Load configuration based on environment
env = 'dev'  # Can be set dynamically or use an environment variable
config = load_config(env)

bp = Blueprint("routes", __name__, static_folder="static")


# SCOPES = 'https://graph.microsoft.com/.default'
# SCOPES = "openid Calendars.ReadWrite.Shared Calendars.ReadBasic Calendars.Read Calendars.ReadWrite Channel.Create Channel.ReadBasic.All Contacts.ReadWrite.Shared email Mail.Read Mail.Read.Shared Mail.ReadBasic Mail.ReadWrite Mail.ReadWrite.Shared Mail.Send Mail.Send.Shared offline_access OnlineMeetings.Read OnlineMeetings.Read.All OnlineMeetings.ReadWrite OnlineMeetings.ReadWrite.All profile Schedule.ReadWrite.All Tasks.Read Tasks.Read.Shared Tasks.ReadWrite Tasks.ReadWrite.Shared User.Read"


@bp.route('/login', methods=['GET'])
async def login():
    # Step 1: Redirect user to Microsoft's authorization page
    params = {
        'client_id': config['CLIENT_ID'],
        'response_type': 'code',
        'redirect_uri': config['REDIRECT_URL'],
        'response_mode': 'query',
        'scope': config['SCOPES'],
        'prompt': 'login'
    }
    return f"{config['AUTHORIZATION_URL']}?{urlencode(params)}"


@bp.route('/callback', methods=['GET'])
async def callback():
    # Step 2: Handle the response from Microsoft
    # data = await request.get_json()
    code ="M.C542_BL2.2.U.b6f00161-23f5-fa5f-cc63-61a41658ec03"
    if not code:
        return "Authorization code not found in the response.",403

    # Step 3: Exchange authorization code for an access token
    token_data = {
        'client_id': config['CLIENT_ID'],
        'redirect_uri': config['REDIRECT_URL'],
        'client_secret': config['CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code',
    }

    # Requesting the access token
    response = requests.post(config['TOKEN_URL'], data=token_data)
    token_json = response.json()

    if 'access_token' not in token_json:
        return f"Error: {token_json.get('error_description', 'Unknown error')}"
    access_token = token_json['access_token']
    return {f"Access Token: {access_token}"},200


@bp.route('/health', methods=['GET'])
async def health_checkup():
    meeting_response = ""
    return success_response("successfully !........", meeting_response)


@bp.route('/get_meetings', methods=['GET'])
async def api_get_meetings():
    try:
        data = await request.get_json()
        get_request = GetMeetingRequest(**data)
        start_date = get_request.start_date
        end_date = get_request.end_date

        if not all([start_date, end_date]):
            return error_response("Missing required parameters", 400)
        # Simulate fetching access token
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
        # Simulate fetching meetings
        meetings_data = await MeetingServices(access_token).get_meetings(config,start_date,end_date)
        # Construct a successful response with the list of meetings
        response_data = GetMeetingResponse(
            status="success",
            message="Meetings retrieved successfully",
            data=meetings_data
        )
        return jsonify(response_data.dict()), 200

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return error_response(str(e), 500)

    except Exception as e:
        # Handle any unexpected errors
        return error_response(str(e), 500)



@bp.route('/create_meeting', methods=['POST'])
async def api_create_meeting():
    try:
        # Parse and validate request data using the CreateMeetingRequest model
        data = await request.get_json()
        meeting_request = CreateMeetingRequest(**data)

        # Access individual attributes from the validated model
        subject = meeting_request.subject
        start_time = meeting_request.start_time
        end_time = meeting_request.end_time
        participants = meeting_request.participants

        # Simulate access token fetching
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)

        # Simulate creating the meeting
        meeting_response_data = await MeetingServices(access_token).create_meeting(
            subject, start_time, end_time, participants, config
        )

        # Validate the response data with CreateMeetingResponse model
        response_data = MeetingResponse(
            status="success",
            message="Meeting created successfully",
            data=meeting_response_data
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400

    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route('/delete_meeting', methods=['DELETE'])
async def api_delete_meeting():
    try:
        # Parse and validate the request data using the DeleteMeetingRequest model
        data = await request.get_json()
        meeting_request = DeleteMeetingRequest(**data)

        # Access individual attributes from the validated model
        meeting_id = meeting_request.meeting_id
        confirmation = meeting_request.confirm

        # Check for missing confirmation
        if confirmation != "yes":
            return error_response("Deletion not confirmed", 400)

        # Simulate fetching access token
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)

        # Simulate deleting the meeting
        deletion_response = await MeetingServices(access_token).delete_meeting(meeting_id, config)

        # Construct a success response
        response_data = MeetingResponse(
            status="success",
            message="Meeting deleted successfully",
            data=deletion_response
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400

    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route('/update_meeting', methods=['PUT'])
async def api_update_meeting():
    try:
        # Parse the request data and validate it against the UpdateMeetingRequest model
        data = await request.get_json()
        meeting_request = UpdateMeetingRequest(**data)

        # Extract fields from the validated request
        meeting_id = meeting_request.meeting_id
        subject = meeting_request.subject
        start_time = meeting_request.start_time
        end_time = meeting_request.end_time
        participants = meeting_request.participants

        # Check for missing fields, but since Pydantic will already validate the required fields, this is optional
        if not all([meeting_id, subject, start_time, end_time, participants]):
            return error_response("Missing required parameters", 400)

        # Attempt to update the meeting using the service
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
        updated_meeting_response = await MeetingServices(access_token).update_meeting(
            meeting_id, subject, start_time, end_time, participants, config
        )

        # Prepare and return the success response
        response_data = MeetingResponse(
            status="success",
            message="Meeting updated successfully",
            data=updated_meeting_response
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic
        return error_response(f"Invalid input: {str(e)}", 400)

    except requests.exceptions.RequestException as e:
        # Handle any errors from external service calls
        return error_response(f"Error with external service: {str(e)}", 500)

    except Exception as e:
        # Catch any other unexpected errors
        return error_response(f"Unexpected error: {str(e)}", 500)


@bp.route('/reschedule_meeting', methods=['PUT'])
async def api_reschedule_meeting():
    try:
        # Parse the request data and validate it using RescheduleMeetingRequest model
        data = await request.get_json()
        meeting_request = RescheduleMeetingRequest(**data)

        # Extract fields from the validated request
        meeting_id = meeting_request.meeting_id
        start_time = meeting_request.start_time
        end_time = meeting_request.end_time

        # Check for missing or invalid fields, but since Pydantic will validate the required fields, this step is optional
        if not meeting_id:
            return error_response("Missing meeting_id parameter", 400)

        if not (start_time and end_time):
            return error_response("Both start_time and end_time are required to reschedule", 400)

        # Attempt to reschedule the meeting using the service
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
        rescheduled_meeting_response = await MeetingServices(access_token).reschedul_meeting(
            meeting_id, None, start_time, end_time, None, config
        )

        # Prepare and return the success response
        response_data = MeetingResponse(
            status="success",
            message="Meeting rescheduled successfully",
            data = rescheduled_meeting_response
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic
        return error_response(f"Invalid input: {str(e)}", 400)

    except requests.exceptions.RequestException as e:
        # Handle any errors from external service calls
        return error_response(f"Error with external service: {str(e)}", 500)

    except Exception as e:
        # Catch any other unexpected errors
        return error_response(f"Unexpected error: {str(e)}", 500)


# Add Participants to Meeting
@bp.route('/add_participants', methods=['PUT'])
async def api_add_participants():
    try:
        # Parse the request data and validate it against the UpdateMeetingRequest model
        data = await request.get_json()
        meeting_request = AddParticipantsRequest(**data)

        # Extract fields from the validated request
        meeting_id = meeting_request.meeting_id
        subject = meeting_request.subject
        participants = meeting_request.participants

        # Check for missing fields, but since Pydantic will already validate the required fields, this is optional
        if not all([meeting_id, subject, participants]):
            return error_response("Missing required parameters", 400)

        # Attempt to update the meeting using the service
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(
            config)
        updated_meeting_response = await MeetingServices(access_token).add_participate_update(
            meeting_id, subject, participants, config
        )

        # Prepare and return the success response
        response_data = MeetingResponse(
            status="success",
            message="Meeting updated successfully",
            data=updated_meeting_response
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic
        return error_response(f"Invalid input: {str(e)}", 400)

    except requests.exceptions.RequestException as e:
        # Handle any errors from external service calls
        return error_response(f"Error with external service: {str(e)}", 500)

    except Exception as e:
        # Catch any other unexpected errors
        return error_response(f"Unexpected error: {str(e)}", 500)


# EMAIL START
@bp.route('/get_email', methods=['GET'])
async def api_get_email():
    try:
        data = await request.get_json()
        get_request = GetEmailRequest(**data)
        start_date = get_request.start_date
        end_date = get_request.end_date

        if not all([start_date, end_date]):
            return error_response("Missing required parameters", 400)

        # Simulate fetching access token
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
        # Simulate fetching meetings
        get_email = await EmailServices(access_token).get_email(config, start_date, end_date)
        # Construct a successful response with the list of meetings
        response_data = GetMeetingResponse(
            status="success",
            message="Email retrieved successfully",
            data=get_email
        )
        return jsonify(response_data.dict()), 200

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return error_response(str(e), 500)

    except Exception as e:
        # Handle any unexpected errors
        return error_response(str(e), 500)


@bp.route('/sent-email', methods=['POST'])
async def create_email():
    try:
        data = await request.get_json()  # FastAPI's equivalent for getting JSON body
        email_request = CreateEmailRequest(**data)  # Validate data with Pydantic model

        # Extract fields from the validated request
        subject = email_request.message.subject
        body_content = email_request.message.body.content
        recipients = [recipient.emailAddress.address for recipient in email_request.message.toRecipients]
        ccRecipients = email_request.message.ccRecipients
        bccRecipients = email_request.message.bccRecipients

        # Check for missing fields, but Pydantic will already enforce required fields
        if not all([subject, body_content, recipients]):
            return error_response("Missing required parameters", 400)

        # Assuming MSFTGraph is your custom class for interacting with the Microsoft Graph API
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(
            config)

        # Make the API call to send the email (example)
        email_sent = await EmailServices(access_token).send_email(subject, body_content, recipients, config, ccRecipients, bccRecipients)
        response_data = MessageSentResponse(
            status="success",
            message="Email sent successfully",
            data=email_sent
        )
        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic
        return error_response(f"Invalid input: {str(e)}", 400)

    except requests.exceptions.RequestException as e:
        # Handle any errors from external service calls
        return error_response(f"Error with external service: {str(e)}", 500)

    except Exception as e:
        # Catch any other unexpected errors
        return error_response(f"Unexpected error: {str(e)}", 500)

@bp.route('/reply_email', methods=['POST'])
async def reply_email():
    try:
        # Parse and validate the incoming request data using the SendEmailRequest model
        data = await request.get_json()
        reply_request = ReplyEmailRequest(**data)

        # Access individual attributes from the validated model
        email_id = reply_request.email_id
        reply_body = reply_request.reply_body

        if not all([email_id, reply_body]):
            return error_response("Missing required parameters", 400)

        # Get the access token for Graph API
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)

        # Simulate sending the email
        reply_sent = await EmailServices(access_token).send_reply(email_id, reply_body, config)

        # Construct a success response
        response_data = MessageSentResponse(
            status="success",
            message="reply response",
            data=reply_sent
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400

    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        return jsonify({"status": "error", "message": str(e)}), 500

    except Exception as e:
        # Catch all other exceptions
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/delete_email', methods=['DELETE'])
async def api_delete_email():
    try:
        # Parse and validate the request data using the DeleteMeetingRequest model
        data = await request.get_json()
        meeting_request = DeleteEmailRequest(**data)

        # Access individual attributes from the validated model
        email_id = meeting_request.email_id
        confirmation = meeting_request.confirm

        # Check for missing confirmation
        if confirmation != "yes":
            return error_response("Deletion not confirmed", 400)

        # Simulate fetching access token
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)

        # Simulate deleting the meeting
        deletion_response = await EmailServices(access_token).delete_email(email_id, config)

        # Construct a success response
        response_data = MeetingResponse(
            status="success",
            message="Meeting deleted successfully",
            data=deletion_response
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400

    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/forwarding_email', methods=['POST'])
async def forwarding_email():
    try:
        # Parse and validate the incoming request data using the SendEmailRequest model
        data = await request.get_json()
        forward_request = ForwardEmailRequest(**data)

        # Access individual attributes from the validated model
        email_id = forward_request.email_id
        forward_to_email = forward_request.forward_to_email
        subject_prefix = forward_request.subject_prefix
        custom_message = forward_request.custom_message

        # Get the access token for Graph API
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)

        # Simulate sending the email
        send_forward_response = await EmailServices(access_token).email_forward(email_id,forward_to_email, subject_prefix, custom_message,config)

        # Construct a success response
        response_data = MeetingResponse(
            status="success",
            message="Forward sent successfully",
            data=send_forward_response
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400

    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        return jsonify({"status": "error", "message": str(e)}), 500

    except Exception as e:
        # Catch all other exceptions
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route('/attachment_email', methods=['POST'])
async def email_with_attachment():
    try:
        # Parse and validate the incoming request data using the SendEmailRequest model
        data = await request.get_json()
        email_request = SendEmailRequest(**data)

        # Access individual attributes from the validated model
        subject = email_request.subject
        body = email_request.body
        recipient_email = email_request.recipient_email
        attachments = email_request.attachments

        # Simulate fetching access token
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)

        # Prepare the attachments (base64 encode the files)
        attachment_data = []
        for file_path in attachments:
            # Read and base64 encode each file
            with open(file_path, "rb") as f:
                file_content = base64.b64encode(f.read()).decode('utf-8')

        # Simulate sending the email
        send_attachment_response = await EmailServices(access_token).\
            email_attachment(subject, body, recipient_email, file_content, config
    )

        # Construct a success response
        response_data = MeetingResponse(
            status="success",
            message="Attachment sent successfully",
            data=send_attachment_response
        )

        return jsonify(response_data.dict()), 200

    except ValidationError as e:
        # Handle validation errors from Pydantic
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400

    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        return jsonify({"status": "error", "message": str(e)}), 500

    except Exception as e:
        # Catch all other exceptions
        return jsonify({"status": "error", "message": str(e)}), 500

# TASK START
@bp.route('/task-get', methods=['GET'])
async def task_find():
    try:
        # Simulate fetching access token
        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
                                 config['TENANT_ID']).get_access_token(config)
        # Simulate fetching meetings
        task_data = await TaskServices(access_token).get_task(config)
        # Construct a successful response with the list of meetings
        response_data = TaskResponse(
            status="success",
            message="Meetings retrieved successfully",
            data=task_data
        )
        return jsonify(response_data.dict()), 200

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return error_response(str(e), 500)

    except Exception as e:
        # Handle any unexpected errors
        return error_response(str(e), 500)

@bp.route('/create-main_task', methods=['POST'])
async def task_create_name():
    try:
        # Simulate fetching access token
        data = await request.get_json()
        displayName_value = TaskCreateHeadingRequest(**data)

        # Access individual attributes from the validated model
        displayName = displayName_value.displayName

        if not all([displayName]):
            return error_response("Missing required parameters", 400)

        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
                                 config['TENANT_ID']).get_access_token(config)
        # Simulate fetching meetings
        task_data = await TaskServices(access_token).creat_task(config, displayName)
        # Construct a successful response with the list of meetings
        response_data = TaskCreateResponse(
            status="success",
            message="Task Create successfully",
            data=task_data
        )
        return jsonify(response_data.dict()), 200

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return error_response(str(e), 500)

    except Exception as e:
        # Handle any unexpected errors
        return error_response(str(e), 500)

@bp.route('/sub_task', methods=['POST'])
async def task_create_sub_name():
    try:
        # Simulate fetching access token
        data = await request.get_json()
        value = TaskCreateSubRequest(**data)

        # Access individual attributes from the validated model
        title = value.title
        todo_list_id = value.todo_list_id

        if not all([title, todo_list_id]):
            return error_response("Missing required parameters", 400)

        access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
                                 config['TENANT_ID']).get_access_token(config)
        # Simulate fetching meetings
        task_data = await TaskServices(access_token).creat_task(config, title)
        # Construct a successful response with the list of meetings
        response_data = TaskCreateResponse(
            status="success",
            message="Task Create successfully",
            data=task_data
        )
        return jsonify(response_data.dict()), 200

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return error_response(str(e), 500)

    except Exception as e:
        # Handle any unexpected errors
        return error_response(str(e), 500)

def create_app():
    app = Quart(__name__)
    app.register_blueprint(bp, url_prefix='/api')  # Register Blueprint for API routes
    return app

