from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Tuple, Optional
from quart import jsonify


class GetEmailRequest(BaseModel):
    start_date: str
    end_date: str

class EmailAddress(BaseModel):
    address: str

class Recipient(BaseModel):
    emailAddress: EmailAddress

class Body(BaseModel):
    contentType: str
    content: str

class GetEmailResponse(BaseModel):
    status: str
    message: str
    data: list

class Message(BaseModel):
    subject: str
    body: Body
    toRecipients: List[Recipient]
    ccRecipients: Optional[List[Recipient]] = None  # Optional CC recipients
    bccRecipients: Optional[List[Recipient]] = None  # Optional BCC recipients

class CreateEmailRequest(BaseModel):
    message: Message

class CreateEmailResponse(BaseModel):
    status: str
    message: str
    data: str

class EmailResponse(BaseModel):
    status: str
    message: str
    data: dict

class DeleteEmailRequest(BaseModel):
    email_id: str
    confirm: str
class DeleteEmailResponse(BaseModel):
    status: str
    message: str
    data: List[dict]

class SendEmailRequest(BaseModel):
    subject: str
    body: str
    recipient_email: str
    attachments: Optional[List[str]] = []  # List of file paths for attachments

class ForwardEmailRequest(BaseModel):
    email_id: str  # The ID of the email to forward
    forward_to_email: str  # The email address to forward the email to
    subject_prefix: Optional[str] = "Fwd:"  # Optional prefix to add to the subject
    custom_message: Optional[str] = None  # Optional custom message to add to the forwarded email

class ReplyEmailRequest(BaseModel):
    email_id: str
    reply_body: str

class MessageSentResponse(BaseModel):
    status: str
    message: str
    data: str
