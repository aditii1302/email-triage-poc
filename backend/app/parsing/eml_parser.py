import email
import hashlib
import os

from email import policy

ATTACHMENT_DIR = "backend/storage/attachments"

os.makedirs(ATTACHMENT_DIR, exist_ok=True)


def generate_conversation_id(msg):

    references = msg.get("References")

    if references:
        return references.strip()

    in_reply_to = msg.get("In-Reply-To")

    if in_reply_to:
        return in_reply_to.strip()

    subject = msg.get("Subject", "")

    normalized_subject = subject.lower().strip()

    return hashlib.sha256(
        normalized_subject.encode()
    ).hexdigest()


def parse_eml(file_path):

    with open(file_path, "rb") as f:

        msg = email.message_from_binary_file(
            f,
            policy=policy.default
        )

    message_id = msg.get("Message-ID")

    subject = msg.get("Subject")

    sender = msg.get("From")

    recipients = msg.get("To")

    cc = msg.get("Cc")

    conversation_id = generate_conversation_id(msg)

    body = ""

    attachments = []

    if msg.is_multipart():

        for part in msg.walk():

            content_disposition = part.get_content_disposition()

            if content_disposition == "attachment":

                filename = part.get_filename()

                file_data = part.get_payload(decode=True)

                save_path = os.path.join(ATTACHMENT_DIR, filename)

                with open(save_path, "wb") as file:
                    file.write(file_data)

                attachments.append(save_path)

            elif part.get_content_type() == "text/plain":

                body += part.get_content()

    else:

        body = msg.get_content()

    return {
        "message_id": message_id,
        "subject": subject,
        "sender": sender,
        "recipients": recipients,
        "cc": cc,
        "body": body,
        "conversation_id": conversation_id,
        "attachments": attachments
    }
