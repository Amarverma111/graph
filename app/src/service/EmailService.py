import base64
from typing import Tuple, Any

import requests
import time
from contracts.email import GetEmailResponse, EmailResponse, MessageSentResponse, DeleteEmailResponse, \
    CreateEmailResponse
from helper.httpclienthelper import HttpHelper, HttpStatusCode


class EmailServices:
    def __init__(self, access_token, config):
        self.access_token = access_token
        self.config = config
        self.headers = {
            self.config['AUTHORIZATION_HEADER']: f"{self.config['BEARER_PREFIX']} {self.access_token}",
            self.config['CONTENT_TYPE_HEADER']: self.config['CONTENT_TYPE']
        }
        self.http_helper = HttpHelper(self.headers)

    async def send_email(self, CreateEmailRequest) -> Tuple[MessageSentResponse, int]:
        email_request = CreateEmailRequest
        subject = email_request.message.subject
        body_content = email_request.message.body.content
        recipients = [recipient.emailAddress.address for recipient in email_request.message.toRecipients]
        ccRecipients = email_request.message.ccRecipients
        bccRecipients = email_request.message.bccRecipients
        # import pdb;pdb.set_trace()
        if not all([subject, body_content, recipients, ccRecipients, bccRecipients]):
            response_data = MessageSentResponse(
                status="error",
                message="Missing required parameters",
                data=""
            )
            return response_data , 403
        """Create a new meeting in the user's calendar."""
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/sendMail"
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body_content
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipients[0]
                        }
                    }
                ]
            }
        }

        if ccRecipients:
            email_data["message"]["ccRecipients"] = [{"emailAddress": {"address": cc.emailAddress.address}} for cc in
                                                     ccRecipients]

        if bccRecipients:
            email_data["message"]["bccRecipients"] = [{"emailAddress": {"address": bcc.emailAddress.address}} for bcc in
                                                      bccRecipients
                                                      ]
        response_data, status = await self.http_helper.post(url, data=email_data)
        # import pdb;pdb.set_trace()
        if response_data.get("status") == "error":
            return MessageSentResponse(
                status="error",
                message=response_data.get("message").get("message", ""),
                data="Error in Email  Sent"
            ), status
        return MessageSentResponse(
            status="success",
            message="Email sent successfully",
            data="Email successfully Sent"
        ), status

    async def get_email(self, GetEmailRequest) -> Tuple[GetEmailResponse, int]:
        start_date = GetEmailRequest.start_date
        end_date = GetEmailRequest.end_date
        if not all([start_date, end_date]):
            # Handle missing parameters case
            response_data = GetEmailResponse(
                status="error",
                message="Missing required parameters",
                data=[]
            )
            return response_data , HttpStatusCode.NOT_FOUND.value  # Return error response with missing parameters
        """Fetch all meetings for the user."""
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/messages?$filter=receivedDateTime ge {start_date}T00:00:00Z and receivedDateTime le {end_date}T23:59:59Z"
        response,status = await self.http_helper.get(url)
        if response.get("status") == "error":
            return GetEmailResponse(
                status="error",
                message=response.get("message").get("message",""),
                data=[]
            ),status
        email = response.get('data', {}).get('value', [])
        AllEmails = []
        for email in email:
            # Collect email details
            email_data = {
                "email_id": email.get("id", "No id"),
                "subject": email.get("subject", "No Subject"),
                "sender": email.get("from", {}).get("emailAddress", {}).get("address", "No Sender"),
                "receivedDateTime": email.get("receivedDateTime", "No Date"),
                "bodyPreview": email.get("bodyPreview", "No Preview")
            }
            AllEmails.append(email_data)

        response_data = GetEmailResponse(
            status="success",
            message="Email retrieved successfully",
            data=AllEmails
        )
        return response_data,status

    async def delete_email(self, DeleteEmailRequest) -> Tuple[DeleteEmailResponse, int]:
        meeting_request = DeleteEmailRequest
        email_id = meeting_request.email_id
        confirmation = meeting_request.confirm
        if confirmation != "yes":
            return DeleteEmailResponse(
                status="error",
                message="Deletion not confirmed because of NO",
                data=[{"message": "Email deletion was not confirmed."}]  # Wrap in a list
            ) ,HttpStatusCode.NOT_FOUND.value
        """Delete a meeting from the user's calendar."""
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/messages/{email_id}"
        response,status = await self.http_helper.delete(url)
        # Check for successful deletion (status code 204)
        if response.get("status") == "error":
            # Return success message when email is successfully deleted
            return DeleteEmailResponse(
                status="error",
                message=response.get("message").get("message",""),
                data=[{}]
            ),status

        return DeleteEmailResponse(
            status="success",
            message=response.get("message").get("message",""),
            data=response
        ),status

    async def email_attachment(self, SendEmailRequest) -> Tuple[EmailResponse, int]:
        email_request = SendEmailRequest
        subject = email_request.subject
        body = email_request.body
        recipient_email = email_request.recipient_email
        attachments = email_request.attachments

        # Validate required parameters
        if not all([body, subject, recipient_email, attachments]):
            response_data = EmailResponse(
                status="error",
                message="Missing required parameters",
                data={}
            )
            return response_data, HttpStatusCode.NOT_FOUND.value

        # Process attachments
        attachment_data = []
        for file_path in attachments:
            try:
                with open(file_path, "rb") as f:
                    file_content = base64.b64encode(f.read()).decode('utf-8')
                    attachment_data.append({
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": file_path.split("/")[-1],  # Extract filename from the path
                        "contentBytes": file_content  # Base64 encoded content
                    })
            except Exception as e:
                response_data = EmailResponse(
                    status="error",
                    message=f"Failed to process attachment {file_path}: {str(e)}",
                    data={}
                )
                return response_data, HttpStatusCode.BAD_REQUEST.value

        # Prepare email data
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/sendMail"
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient_email
                        }
                    }
                ],
                "attachments": attachment_data
            },
            "saveToSentItems": "true"  # Save the sent email to Sent Items
        }

        # Send the email
        response_data, status = await self.http_helper.post(url, data=email_data)
        if response_data.get("status") == "error":
            return EmailResponse(
                status="error",
                message=response_data.get("message", {}).get("message", ""),
                data={}
            ), status

        return EmailResponse(
            status="success",
            message="Attachment sent successfully",
            data=response_data
        ), status

    async def email_forward(self, ForwardEmailRequest) -> Tuple[EmailResponse, int]:
        forward_request = ForwardEmailRequest
        # Access individual attributes from the validated model
        email_id = forward_request.email_id
        forward_to_email = forward_request.forward_to_email
        subject_prefix = forward_request.subject_prefix
        custom_message = forward_request.custom_message
        if not all([email_id, forward_to_email, subject_prefix, custom_message]):
            response_data = EmailResponse(
                status="error",
                message="Missing required parameters",
                data={}
            )
            return response_data,HttpStatusCode.NOT_FOUND.value

        global forward_response, forward_url
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/messages/{email_id}"
        response,status = await self.http_helper.get(url)
        # import pdb;pdb.set_trace()
        if response.get("status") == "error":
            raise Exception(f"Failed to fetch the email: {response.text}")
        email = response.get("data")
        # Prepare the forwarded email content
        forwarded_subject = f"{subject_prefix} {email['subject']}"
        forwarded_body = f"Forwarded message:\n\n{email['bodyPreview']}\n\n--- Original Message ---\n{email['body']['content']}"

        # If custom message is provided, prepend it to the forwarded content
        if custom_message:
            forwarded_body = f"{custom_message}\n\n{forwarded_body}"

        # Prepare the forward email data
        forward_email_data = {
            "message": {
                "subject": forwarded_subject,
                "body": {
                    "contentType": "HTML",
                    "content": forwarded_body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": forward_to_email
                        }
                    }
                ],
                "attachments": []  # You can add attachment logic here
            },
            "saveToSentItems": "true"
        }
        while True:
            try:
                # Corrected method call: remove the extra 'self' argument
                response,status =  await self.repeater_api(forward_email_data)
                if status == 429:
                    return EmailResponse(
                        status="error",
                        message= response.get("error").get("message",""),
                        data={}
                    ),status
                return EmailResponse(
                    status="success",
                    message="Forward sent successfully",
                    data=response
                ),status
            except requests.exceptions.RequestException as e:
                print(f"Request failed with error: {e}, retrying...")

            # Wait before retrying
            time.sleep(10)

    async def repeater_api(self, forward_email_data):
        forward_url = f"{self.config['GRAPH_API_ENDPOINT']}/me/sendMail"
        forward_response = requests.post(forward_url, json=forward_email_data, headers=self.headers)
        return forward_response.json(),forward_response.status_code

    # async def reply_email(self, email_id, reply_body, config):
    #     """Create a new meeting in the user's calendar."""
    #     url = f"{config['GRAPH_API_ENDPOINT']}/me/messages/{email_id}/reply"
    #     # The body of the reply
    #     data = {
    #         "message": {
    #             "body": {
    #                 "contentType": "Text",
    #                 "content": reply_body
    #             }
    #         }
    #     }
    #
    #     # response = requests.post(url, headers=self.headers, json=data)
    #     # response.raise_for_status()
    #     # return "completed"
    #     max_retries = 5
    #     retry_count = 0
    #     backoff_time = 1  # Initial backoff time in seconds
    #
    #
    #     while retry_count < max_retries:
    #         response = requests.post(url, headers=self.headers, json=data)
    #
    #         if response.status_code == 429:
    #             retry_after = int(response.headers.get("Retry-After", backoff_time))
    #             print(f"Too many requests. Retrying after {retry_after} seconds.")
    #             time.sleep(retry_after)
    #             backoff_time = min(backoff_time * 2, 32)  # Exponential backoff with a max cap
    #             retry_count += 1
    #             return "completed"
    #         else:
    #             return response

    async def send_reply(self, ReplyEmailRequest) -> Tuple[CreateEmailResponse, int]:
        # Access individual attributes from the validated model
        email_id = ReplyEmailRequest.email_id
        reply_body = ReplyEmailRequest.reply_body
        if not all([email_id, reply_body]):
            return CreateEmailResponse(
                status="error",
                message="Missing required parameters",
                data=""
            ),403
        """Create a new reply to the user's email."""
        url = f"{self.config['GRAPH_API_ENDPOINT']}/me/messages/{email_id}/reply"

        # The body of the reply
        data = {
            "message": {
                "body": {
                    "contentType": "Text",
                    "content": reply_body
                }
            }
        }
        response_data,status = await self.http_helper.post(url, data=data)
        if response_data.get("status") == "error":
            return CreateEmailResponse(
                status="error",
                message=response_data.get("message").get("message",""),
                data="Reply not sent"
            ),status
        return CreateEmailResponse(
            status="success",
            message="reply response",
            data="Reply sent"
        ),status
