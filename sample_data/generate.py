import os
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from faker import Faker
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw

fake = Faker()
random.seed(42)
OUTPUT_DIR = 'sample_data/emails'
ATTACH_DIR = 'sample_data/attachments'
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ATTACH_DIR, exist_ok=True)
APPS = ['HR Portal', 'Finance System', 'VPN Client', 'Employee Portal', 'Payroll System', 'Email System', 'SharePoint']
SUPPORT_DL = 'support@example.com'
DOMAINS = ['example.com', 'corp.example.com']
counter = [0]

def make_user():
    name = fake.name()
    email = fake.user_name() + '@' + random.choice(DOMAINS)
    return name, email

def next_name():
    counter[0] += 1
    return f'email_{counter[0]:03d}.eml'

def save_eml(msg, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w') as f:
        f.write(msg.as_string())
    return path

def make_eml(subject, body, from_addr, to_addr, attachments=None, reply_to=None):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg['Message-ID'] = f'<{fake.uuid4()}@example.com>'
    if reply_to:
        msg['In-Reply-To'] = reply_to
        msg['References'] = reply_to
    msg.attach(MIMEText(body, 'plain'))
    if attachments:
        for filepath in attachments:
            with open(filepath, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filepath)}')
                msg.attach(part)
    return msg

def make_pdf(filename, text):
    path = os.path.join(ATTACH_DIR, filename)
    c = canvas.Canvas(path)
    c.drawString(100, 750, 'Error Log')
    y = 720
    for line in text.split('\n'):
        c.drawString(100, y, line)
        y -= 20
    c.save()
    return path

def make_png(filename, text):
    path = os.path.join(ATTACH_DIR, filename)
    img = Image.new('RGB', (600, 300), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 580, 280], fill='white', outline='red', width=2)
    draw.text((30, 30), 'ERROR DIALOG', fill='red')
    y = 70
    for line in text.split('\n'):
        draw.text((30, y), line, fill='black')
        y += 25
    img.save(path)
    return path

# 1. 10 clear actionable issues
apps_sample = random.sample(APPS, 7)
for i in range(10):
    name, email = make_user()
    app = apps_sample[i % len(apps_sample)]
    body = f'Hi team,\n\nI am unable to access {app}. Getting an error when logging in. Please assist.\n\nRegards,\n{name}'
    msg = make_eml(f'Issue with {app}', body, email, SUPPORT_DL)
    save_eml(msg, next_name())

# 2. 5 with PDF attachments
for i in range(5):
    name, email = make_user()
    app = random.choice(APPS)
    pdf_text = f'Application: {app}\nError Code: ERR-{random.randint(100,999)}\nUser: {email}\nDescription: System failed'
    pdf_path = make_pdf(f'error_log_{i+1}.pdf', pdf_text)
    body = f'Hi,\n\nPlease find the error log from {app} attached.\n\nThanks,\n{name}'
    msg = make_eml(f'Error log - {app}', body, email, SUPPORT_DL, attachments=[pdf_path])
    save_eml(msg, next_name())

# 3. 5 with screenshot attachments
for i in range(5):
    name, email = make_user()
    app = random.choice(APPS)
    png_text = f'Application: {app}\nError: AUTH-{random.randint(100,999)}\nUser: {email}'
    png_path = make_png(f'screenshot_{i+1}.png', png_text)
    body = f'Hi,\n\nScreenshot of error in {app} attached.\n\nRegards,\n{name}'
    msg = make_eml(f'Screenshot - {app}', body, email, SUPPORT_DL, attachments=[png_path])
    save_eml(msg, next_name())

# 4. 5 multi-email threads
for i in range(5):
    name, email = make_user()
    app = random.choice(APPS)
    first_id = f'<thread-{i+1}@example.com>'
    body1 = f'Hi,\n\nChecking on my request about {app}.\n\nThanks,\n{name}'
    msg1 = make_eml(f'Re: Follow up on {app}', body1, email, SUPPORT_DL)
    msg1.replace_header('Message-ID', first_id)
    save_eml(msg1, next_name())
    body2 = f'Hi,\n\nStill cannot access {app}. Error SYS-500. This is urgent.\n\nRegards,\n{name}'
    msg2 = make_eml(f'Re: Follow up on {app}', body2, email, SUPPORT_DL, reply_to=first_id)
    save_eml(msg2, next_name())

# 5. 5 near-duplicates HIGH band
base_name, base_email = make_user()
base_app = 'HR Portal'
phrases = [
    'I cannot log into HR Portal. Getting AUTH-401 error.',
    'Login is failing on HR Portal with error AUTH-401.',
    'HR Portal is showing AUTH-401 when I try to sign in.',
    'Unable to authenticate on HR Portal, error AUTH-401 appears.',
    'Getting AUTH-401 on HR Portal login page.',
]
for i in range(5):
    body = f'Hi,\n\n{phrases[i]}\n\nPlease help.\n\n{base_name}'
    msg = make_eml('Cannot access HR Portal', body, base_email, SUPPORT_DL)
    save_eml(msg, next_name())

# 6. 5 borderline duplicates LOW band
for i in range(5):
    name, email = make_user()
    body = f'Hi,\n\nHaving trouble with HR Portal. Not sure what is happening but I cannot get in.\n\nThanks,\n{name}'
    msg = make_eml('Problem with HR Portal', body, email, SUPPORT_DL)
    save_eml(msg, next_name())

# 7. 5 non-actionable
non_actionable = [
    ('Team Newsletter', 'Hi all, please find this months newsletter. Best regards, HR Team'),
    ('Re: Thanks!', 'Just wanted to say thanks for resolving my issue! All working now.'),
    ('FYI - Maintenance tonight', 'Maintenance tonight from 10pm to 2am. No action needed.'),
    ('Meeting invite: Q3 Planning', 'You are invited to Q3 planning meeting on Friday at 2pm.'),
    ('Out of office', 'I am out of office and will return next Monday.'),
]
for subject, body in non_actionable:
    name, email = make_user()
    msg = make_eml(subject, body, email, SUPPORT_DL)
    save_eml(msg, next_name())

print(f'Generated {counter[0]} emails in {OUTPUT_DIR}')
