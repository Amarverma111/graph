import requests
import base64
from quart import (Blueprint, Quart, request, jsonify)
from service.MeetingService import MeetingServices
from service.extension.load_config_yaml import load_config
from service.EmailService import EmailServices
from service.TaskService import TaskServices
from service.whoamiservice import WhoAmIService
from helper.httpclienthelper import HttpStatusCode
from pydantic import ValidationError
from urllib.parse import urlencode
from contracts.meeting import CreateMeetingRequest, MeetingResponse, DeleteMeetingRequest, UpdateMeetingRequest, RescheduleMeetingRequest,\
    AddParticipantsRequest,  GetMeetingResponse, GetMeetingRequest, DeleteMeetingResponse
from contracts.email import CreateEmailRequest, DeleteEmailRequest, SendEmailRequest, ForwardEmailRequest, ReplyEmailRequest, MessageSentResponse, GetEmailRequest
from contracts.task import TaskResponse, TaskCreateHeadingRequest, TaskCreateSubRequest, TaskCreateResponse, \
    TaskGeTSubRequest



# Load configuration based on environment
env = 'dev'  # Can be set dynamically or use an environment variable
config = load_config(env)

bp = Blueprint("routes", __name__, static_folder="static")


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
    return f"{config['AUTHORIZATION_URL']}?{urlencode(params)}", 200


@bp.route('/callback', methods=['GET'])
async def callback():
    # Step 2: Handle the response from Microsoft
    # data = await request.get_json()
    code ="M.C542_BAY.2.U.e325a680-11e8-cdf0-c0ef-9df1cb62c362"
    if not code:
        return "Authorization code not found in the response.", 403

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
        return f"Error: {token_json.get('error_description', 'Unknown error')}", 401
    access_token = token_json['access_token']
    return f"Access Token: {access_token}", 200


@bp.route('/health', methods=['GET'])
async def health_checkup():
    try:
        response = MeetingResponse(
            status="success",
            message="API IS WORKING FINE !",
            data={})
        return jsonify(response.model_dump()), HttpStatusCode.OK.value
    except Exception as e:
        response = MeetingResponse(
            status="error",
            message="API IS NOT WORKING!",
            data={})
        return jsonify(response.model_dump()), HttpStatusCode.INTERNAL_SERVER_ERROR.value


@bp.route('/get_meetings', methods=['GET'])
async def api_get_meetings():
    try:
        data = await request.get_json()
        headers = request.headers
        access_token = WhoAmIService(headers, config).get_access_token()
        meetings_data,status_code = await MeetingServices(access_token, config).get_meetings(GetMeetingRequest(**data))
        # Construct the successful response with the list of meetings
        if status_code == 200:
            return jsonify(meetings_data.model_dump()), status_code
        else:
            return jsonify(meetings_data.model_dump()), status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), HttpStatusCode.INTERNAL_SERVER_ERROR.value


@bp.route('/create_meeting', methods=['POST'])
async def api_create_meeting():
    try:
        # Parse and validate request data using the CreateMeetingRequest model
        data = await request.get_json()
        headers = request.headers
        # Simulate access token fetching
        access_token = WhoAmIService(headers, config).get_access_token()
        # Simulate creating the meeting
        meeting_response_data,status_code = await MeetingServices(access_token, config).create_meeting(CreateMeetingRequest(**data))
        if status_code == 200:
            #  Return the response from the create_meeting method, which includes success or error message
            return jsonify(meeting_response_data.model_dump()), status_code
        else:
            return jsonify(meeting_response_data.model_dump()), status_code
    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), HttpStatusCode.BAD_REQUEST.value



@bp.route('/delete_meeting', methods=['DELETE'])
async def api_delete_meeting():
    try:
        # Parse and validate the request data using the DeleteMeetingRequest model
        data = await request.get_json()
        headers = request.headers
        # Simulate access token fetching
        access_token = WhoAmIService(headers, config).get_access_token()
        # Simulate deleting the meeting
        deletion_response,status_code = await MeetingServices(access_token, config).delete_meeting(DeleteMeetingRequest(**data))
        if status_code == 200:
            # Convert deletion_response to a dictionary before returning it
            response_data = DeleteMeetingResponse(
                status="success",
                message="Meeting deleted successfully",
                data=[deletion_response.model_dump()]  # Convert to dict here
            )

            return jsonify(response_data.model_dump()), status_code
        else:
            response_data = DeleteMeetingResponse(
                status="error",
                message="Issue deletion",
                data=[deletion_response.model_dump()]  # Convert to dict here
            )

            return jsonify(response_data.model_dump()), status_code
    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), HttpStatusCode.BAD_REQUEST.value



@bp.route('/update_meeting', methods=['PUT'])
async def api_update_meeting():
    try:
        # Parse the request data and validate it against the UpdateMeetingRequest model
        data = await request.get_json()        # Attempt to update the meeting using the service
        headers = request.headers
        # Simulate access token fetching
        access_token = WhoAmIService(headers, config).get_access_token()
        updated_meeting_response,status_code = await MeetingServices(access_token, config).update_meeting(UpdateMeetingRequest(**data))
        if status_code == 200:
            # Return the response from the create_meeting method, which includes success or error message
            return jsonify(updated_meeting_response.model_dump()),status_code
        else:
            return jsonify(updated_meeting_response.model_dump()), status_code

    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), HttpStatusCode.BAD_REQUEST.value


@bp.route('/reschedule_meeting', methods=['PUT'])
async def api_reschedule_meeting():
    try:
        data = await request.get_json()  # Attempt to update the meeting using the service
        headers = request.headers
        # Simulate access token fetching
        access_token = WhoAmIService(headers, config).get_access_token()
        rescheduled_meeting_response,status_code = await MeetingServices(access_token, config).reschedule_meeting(RescheduleMeetingRequest(**data))
        if status_code == 200:
            # Return the response from the create_meeting method, which includes success or error message
            return jsonify(rescheduled_meeting_response.model_dump()), status_code
        else:
            return jsonify(rescheduled_meeting_response.model_dump()), status_code

    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), HttpStatusCode.BAD_REQUEST


# Add Participants to Meeting
@bp.route('/add_participants', methods=['PUT'])
async def api_add_participants():
    try:
        # Parse the request data and validate it against the UpdateMeetingRequest model
        data = await request.get_json()  # Attempt to update the meeting using the service
        headers = request.headers
        # Simulate access token fetching
        access_token = WhoAmIService(headers, config).get_access_token()
        updated_meeting_response,status_code = await MeetingServices(access_token, config).add_participate_update(AddParticipantsRequest(**data))
        if status_code == 200:
            return jsonify(updated_meeting_response.model_dump()), status_code
        else:
            return jsonify(updated_meeting_response.model_dump()),status_code
    except ValidationError as e:
        # Handle validation errors from Pydantic, including missing fields
        return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), HttpStatusCode.BAD_REQUEST.value



# # EMAIL START
# @bp.route('/get_email', methods=['GET'])
# async def api_get_email():
#     try:
#         data = await request.get_json()
#         get_request = GetEmailRequest(**data)
#         start_date = get_request.start_date
#         end_date = get_request.end_date
#
#         if not all([start_date, end_date]):
#             return error_response("Missing required parameters", 400)
#
#         # Simulate fetching access token
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
#         # Simulate fetching meetings
#         get_email = await EmailServices(access_token).get_email(config, start_date, end_date)
#         # Construct a successful response with the list of meetings
#         response_data = GetMeetingResponse(
#             status="success",
#             message="Email retrieved successfully",
#             data=get_email
#         )
#         return jsonify(response_data.model_dump()), 200
#
#     except requests.exceptions.RequestException as e:
#         # Handle request exceptions
#         return error_response(str(e), 500)
#
#     except Exception as e:
#         # Handle any unexpected errors
#         return error_response(str(e), 500)
#
#
# @bp.route('/sent-email', methods=['POST'])
# async def create_email():
#     try:
#         data = await request.get_json()  # FastAPI's equivalent for getting JSON body
#         email_request = CreateEmailRequest(**data)  # Validate data with Pydantic model
#
#         # Extract fields from the validated request
#         subject = email_request.message.subject
#         body_content = email_request.message.body.content
#         recipients = [recipient.emailAddress.address for recipient in email_request.message.toRecipients]
#         ccRecipients = email_request.message.ccRecipients
#         bccRecipients = email_request.message.bccRecipients
#
#         # Check for missing fields, but Pydantic will already enforce required fields
#         if not all([subject, body_content, recipients]):
#             return error_response("Missing required parameters", 400)
#
#         # Assuming MSFTGraph is your custom class for interacting with the Microsoft Graph API
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(
#             config)
#
#         # Make the API call to send the email (example)
#         email_sent = await EmailServices(access_token).send_email(subject, body_content, recipients, config, ccRecipients, bccRecipients)
#         response_data = MessageSentResponse(
#             status="success",
#             message="Email sent successfully",
#             data=email_sent
#         )
#         return jsonify(response_data.dict()), 200
#
#     except ValidationError as e:
#         # Handle validation errors from Pydantic
#         return error_response(f"Invalid input: {str(e)}", 400)
#
#     except requests.exceptions.RequestException as e:
#         # Handle any errors from external service calls
#         return error_response(f"Error with external service: {str(e)}", 500)
#
#     except Exception as e:
#         # Catch any other unexpected errors
#         return error_response(f"Unexpected error: {str(e)}", 500)
#
# @bp.route('/reply_email', methods=['POST'])
# async def reply_email():
#     try:
#         # Parse and validate the incoming request data using the SendEmailRequest model
#         data = await request.get_json()
#         reply_request = ReplyEmailRequest(**data)
#
#         # Access individual attributes from the validated model
#         email_id = reply_request.email_id
#         reply_body = reply_request.reply_body
#
#         if not all([email_id, reply_body]):
#             return error_response("Missing required parameters", 400)
#
#         # Get the access token for Graph API
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
#
#         # Simulate sending the email
#         reply_sent = await EmailServices(access_token).send_reply(email_id, reply_body, config)
#
#         # Construct a success response
#         response_data = MessageSentResponse(
#             status="success",
#             message="reply response",
#             data=reply_sent
#         )
#
#         return jsonify(response_data.dict()), 200
#
#     except ValidationError as e:
#         # Handle validation errors from Pydantic
#         return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400
#
#     except requests.exceptions.RequestException as e:
#         # Handle any request exceptions
#         return jsonify({"status": "error", "message": str(e)}), 500
#
#     except Exception as e:
#         # Catch all other exceptions
#         return jsonify({"status": "error", "message": str(e)}), 500
#
# @bp.route('/delete_email', methods=['DELETE'])
# async def api_delete_email():
#     try:
#         # Parse and validate the request data using the DeleteMeetingRequest model
#         data = await request.get_json()
#         meeting_request = DeleteEmailRequest(**data)
#
#         # Access individual attributes from the validated model
#         email_id = meeting_request.email_id
#         confirmation = meeting_request.confirm
#
#         # Check for missing confirmation
#         if confirmation != "yes":
#             return error_response("Deletion not confirmed", 400)
#
#         # Simulate fetching access token
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
#
#         # Simulate deleting the meeting
#         deletion_response = await EmailServices(access_token).delete_email(email_id, config)
#
#         # Construct a success response
#         response_data = MeetingResponse(
#             status="success",
#             message="Meeting deleted successfully",
#             data=deletion_response
#         )
#
#         return jsonify(response_data.dict()), 200
#
#     except ValidationError as e:
#         # Handle validation errors from Pydantic, including missing fields
#         return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400
#
#     except requests.exceptions.RequestException as e:
#         # Handle any request exceptions
#         return jsonify({"status": "error", "message": str(e)}), 500
#
# @bp.route('/forwarding_email', methods=['POST'])
# async def forwarding_email():
#     try:
#         # Parse and validate the incoming request data using the SendEmailRequest model
#         data = await request.get_json()
#         forward_request = ForwardEmailRequest(**data)
#
#         # Access individual attributes from the validated model
#         email_id = forward_request.email_id
#         forward_to_email = forward_request.forward_to_email
#         subject_prefix = forward_request.subject_prefix
#         custom_message = forward_request.custom_message
#
#         # Get the access token for Graph API
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
#
#         # Simulate sending the email
#         send_forward_response = await EmailServices(access_token).email_forward(email_id,forward_to_email, subject_prefix, custom_message,config)
#
#         # Construct a success response
#         response_data = MeetingResponse(
#             status="success",
#             message="Forward sent successfully",
#             data=send_forward_response
#         )
#
#         return jsonify(response_data.dict()), 200
#
#     except ValidationError as e:
#         # Handle validation errors from Pydantic
#         return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400
#
#     except requests.exceptions.RequestException as e:
#         # Handle any request exceptions
#         return jsonify({"status": "error", "message": str(e)}), 500
#
#     except Exception as e:
#         # Catch all other exceptions
#         return jsonify({"status": "error", "message": str(e)}), 500
#
#
# @bp.route('/attachment_email', methods=['POST'])
# async def email_with_attachment():
#     try:
#         # Parse and validate the incoming request data using the SendEmailRequest model
#         data = await request.get_json()
#         email_request = SendEmailRequest(**data)
#
#         # Access individual attributes from the validated model
#         subject = email_request.subject
#         body = email_request.body
#         recipient_email = email_request.recipient_email
#         attachments = email_request.attachments
#
#         # Simulate fetching access token
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'], config['TENANT_ID']).get_access_token(config)
#
#         # Prepare the attachments (base64 encode the files)
#         attachment_data = []
#         for file_path in attachments:
#             # Read and base64 encode each file
#             with open(file_path, "rb") as f:
#                 file_content = base64.b64encode(f.read()).decode('utf-8')
#
#         # Simulate sending the email
#         send_attachment_response = await EmailServices(access_token).\
#             email_attachment(subject, body, recipient_email, file_content, config
#     )
#
#         # Construct a success response
#         response_data = MeetingResponse(
#             status="success",
#             message="Attachment sent successfully",
#             data=send_attachment_response
#         )
#
#         return jsonify(response_data.dict()), 200
#
#     except ValidationError as e:
#         # Handle validation errors from Pydantic
#         return jsonify({"status": "error", "message": "Invalid data: " + str(e)}), 400
#
#     except requests.exceptions.RequestException as e:
#         # Handle any request exceptions
#         return jsonify({"status": "error", "message": str(e)}), 500
#
#     except Exception as e:
#         # Catch all other exceptions
#         return jsonify({"status": "error", "message": str(e)}), 500
#
# # TASK START
# @bp.route('/get_all_task', methods=['GET'])
# async def task_find():
#     try:
#         # Simulate fetching access token
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
#                                  config['TENANT_ID']).get_access_token(config)
#         # Simulate fetching meetings
#         task_data = await TaskServices(access_token).get_task(config)
#         # Construct a successful response with the list of meetings
#         response_data = TaskResponse(
#             status="success",
#             message="Task retrieved successfully",
#             data=task_data
#         )
#         return jsonify(response_data.dict()), 200
#
#     except requests.exceptions.RequestException as e:
#         # Handle request exceptions
#         return error_response(str(e), 500)
#
#     except Exception as e:
#         # Handle any unexpected errors
#         return error_response(str(e), 500)
#
#
# @bp.route('/get_sub_task', methods=['GET'])
# async def task_findss():
#     try:
#         data = await request.get_json()
#         value = TaskGeTSubRequest(**data)
#
#         # Access individual attributes from the validated model
#         todo_list_id = value.todo_list_id
#         taskId = value.taskId
#
#
#         if not all([todo_list_id]):
#             return error_response("Missing required parameters", 400)
#         # Simulate fetching access token
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
#                                  config['TENANT_ID']).get_access_token(config)
#         # Simulate fetching meetings
#         task_data = await TaskServices(access_token).get_sub_task(config,taskId,todo_list_id)
#         # Construct a successful response with the list of meetings
#         response_data = TaskResponse(
#             status="success",
#             message="sub task retrieved successfully",
#             data=task_data
#         )
#         return jsonify(response_data.dict()), 200
#
#     except requests.exceptions.RequestException as e:
#         # Handle request exceptions
#         return error_response(str(e), 500)
#
#     except Exception as e:
#         # Handle any unexpected errors
#         return error_response(str(e), 500)
#
#
#
# @bp.route('/create-main_task', methods=['POST'])
# async def task_create_name():
#     try:
#         # Simulate fetching access token
#         data = await request.get_json()
#         displayName_value = TaskCreateHeadingRequest(**data)
#
#         # Access individual attributes from the validated model
#         displayName = displayName_value.displayName
#
#         if not all([displayName]):
#             return error_response("Missing required parameters", 400)
#
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
#                                  config['TENANT_ID']).get_access_token(config)
#         # Simulate fetching meetings
#         task_data = await TaskServices(access_token).creat_task(config, displayName)
#         # Construct a successful response with the list of meetings
#         response_data = TaskCreateResponse(
#             status="success",
#             message="Task Create successfully",
#             data=task_data
#         )
#         return jsonify(response_data.dict()), 200
#
#     except requests.exceptions.RequestException as e:
#         # Handle request exceptions
#         return error_response(str(e), 500)
#
#     except Exception as e:
#         # Handle any unexpected errors
#         return error_response(str(e), 500)
#
# @bp.route('/create_sub_task', methods=['POST'])
# async def task_create_sub_name():
#     try:
#         # Simulate fetching access token
#         data = await request.get_json()
#         value = TaskCreateSubRequest(**data)
#
#         # Access individual attributes from the validated model
#         title = value.title
#         todo_list_id = value.todo_list_id
#
#         if not all([title, todo_list_id]):
#             return error_response("Missing required parameters", 400)
#
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
#                                  config['TENANT_ID']).get_access_token(config)
#         # Simulate fetching meetings
#         task_data = await TaskServices(access_token).create_sub_task(config, title, todo_list_id)
#         # Construct a successful response with the list of meetings
#         response_data = TaskCreateResponse(
#             status="success",
#             message="Sub Task Create successfully",
#             data=task_data
#         )
#         return jsonify(response_data.dict()), 200
#
#     except requests.exceptions.RequestException as e:
#         # Handle request exceptions
#         return error_response(str(e), 500)
#
#     except Exception as e:
#         # Handle any unexpected errors
#         return error_response(str(e), 500)
#
# @bp.route('/delete-task', methods=['delete'])
# async def task_find_delete():
#     try:
#         # Simulate fetching access token
#         access_token = MSFTGraph(config['CLIENT_ID'], config['CLIENT_SECRET'],
#                                  config['TENANT_ID']).get_access_token(config)
#         # Simulate fetching meetings
#         task_data = await TaskServices(access_token).delete_task(config)
#         # Construct a successful response with the list of meetings
#         response_data = TaskResponse(
#             status="success",
#             message="Meetings retrieved successfully",
#             data=task_data
#         )
#         return jsonify(response_data.dict()), 200
#
#     except requests.exceptions.RequestException as e:
#         # Handle request exceptions
#         return error_response(str(e), 500)
#
#     except Exception as e:
#         # Handle any unexpected errors
#         return error_response(str(e), 500)


def create_app():
    app = Quart(__name__)
    app.register_blueprint(bp, url_prefix='/api')  # Register Blueprint for API routes
    return app

