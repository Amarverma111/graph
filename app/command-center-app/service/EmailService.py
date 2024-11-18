import requests
from requests.exceptions import HTTPError, RequestException
import time

class EmailServices:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def send_email(self, subject, body_content, recipients, config,  ccRecipients, bccRecipients):
        """Create a new meeting in the user's calendar."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/sendMail"
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
            email_data["message"]["ccRecipients"] = [{"emailAddress": {"address": cc.emailAddress.address}} for cc in ccRecipients]

        if bccRecipients:
            email_data["message"]["bccRecipients"] = [{"emailAddress": {"address": bcc.emailAddress.address}} for bcc in bccRecipients
            ]
        response = requests.post(url, headers=self.headers, json=email_data)
        response.raise_for_status()
        return "Message sent completed"

    async def get_email(self, config):
        """Fetch all meetings for the user."""
        AllEmails =[]
        url = f"{config['GRAPH_API_ENDPOINT']}/me/messages"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        email = response.json().get('value', [])
        for email in email:
            # Collect email details
            email_data = {
                "email_id": email.get("id","No id"),
                "subject": email.get("subject", "No Subject"),
                "sender": email.get("from", {}).get("emailAddress", {}).get("address", "No Sender"),
                "receivedDateTime": email.get("receivedDateTime", "No Date"),
                "bodyPreview": email.get("bodyPreview", "No Preview")
            }
            AllEmails.append(email_data)

        return AllEmails


    async def delete_email(self, message_id, config):
        """Delete a meeting from the user's calendar."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/messages/{message_id}"
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            return {"message": "Email deleted successfully"}
        else:
            response.raise_for_status()


    async def email_attachment(self,subject,body,recipient_email, file_content,config ):
        url = f"{config['GRAPH_API_ENDPOINT']}/me/sendMail"
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
                "attachments": [
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": "example.pdf",  # The name that the recipient will see
                        "contentBytes": file_content  # Base64 encoded PDF content
                    }
                ]
            },
            "saveToSentItems": "true"  # Save the sent email to Sent Items
        }
        import pdb;pdb.set_trace()
        response = requests.post(url, headers=self.headers, json=email_data)
        response.raise_for_status()
        return response.json()

    async def email_forward(self, email_id,forward_to_email, subject_prefix, custom_message,config):
        global forward_response, forward_url
        url = f"{config['GRAPH_API_ENDPOINT']}/me/messages/{email_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the email: {response.text}")
        email = response.json()
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
                response = self.repeater_api(config, forward_email_data)

                # Check if response has a 200 status code or other condition
                if response['statusCode'] == 200:
                    print("Request successful.")
                    return response
                else:
                    print("Unexpected status code, retrying...")
            except requests.exceptions.RequestException as e:
                print(f"Request failed with error: {e}, retrying...")

            # Wait before retrying
            time.sleep(10)

    async def repeater_api(self, config, forward_email_data):
        forward_url = f"{config['GRAPH_API_ENDPOINT']}/me/sendMail"
        forward_response = requests.post(forward_url, json=forward_email_data, headers=self.headers)
        forward_response.raise_for_status()
        return forward_response.json()




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


    async def send_reply(self, email_id, reply_body, config):
        """Create a new reply to the user's email."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/messages/{email_id}/reply"

        # The body of the reply
        data = {
            "message": {
                "body": {
                    "contentType": "Text",
                    "content": reply_body
                }
            }
        }

        max_retries = 5
        retry_count = 0
        backoff_time = 1  # Initial backoff time in seconds

        while retry_count < max_retries:
            response = requests.post(url, headers=self.headers, json=data)

            if response.status_code == 429:
                # When rate-limited, read the 'Retry-After' header and wait
                retry_after = int(response.headers.get("Retry-After", backoff_time))
                print(f"Too many requests. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                backoff_time = min(backoff_time * 2, 32)  # Exponential backoff with a max cap
                retry_count += 1
            elif response.status_code == 202:
                # HTTP 202 indicates the reply was accepted
                return "Reply sent"
            else:
                # If we get any other error code, handle it (e.g., 400, 401, 500, etc.)
                print(f"Error sending reply: {response.status_code} - {response.text}")
                return "Failed to send reply"

        # If we exhaust retries and still get 429 errors or other failures, return not sent
        return "Reply not sent after retries"

