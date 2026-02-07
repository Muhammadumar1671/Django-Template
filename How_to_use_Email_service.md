# Email Service Documentation

A flexible, generic email service with support for multiple providers, database templates, and signal-based email triggering.

## Features

- ✅ **Multiple Providers**: SendGrid, Resend, or SMTP
- ✅ **Template Management**: Database or static file templates
- ✅ **Signal-Based**: Single generic signal for all email actions
- ✅ **Email Logging**: Track all sent emails
- ✅ **Easy Configuration**: Environment-based settings

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Global email enable/disable
EMAIL_ENABLED=True

# Email provider
EMAIL_PROVIDER=smtp  # Options: smtp, sendgrid, resend

# API key (required for sendgrid/resend)
EMAIL_PROVIDER_API_KEY=your-api-key-here

# Sender details
DEFAULT_FROM_EMAIL=noreply@example.com
DEFAULT_FROM_NAME=Your App

# Template source
USE_DB_EMAIL_TEMPLATES=db  # Options: db, static, db_only

# Frontend configuration
FRONTEND_URL=http://localhost:3000
SITE_NAME=Your App Name
```

### Template Source Options

- **`db`** (default): Try database templates first, fallback to static files
- **`static`**: Only use static template files
- **`db_only`**: Only use database templates (raises error if not found)

---

## Usage

### 1. Using Signals (Recommended)

The email service provides a single, generic signal for all email actions.

#### Basic Usage

```python
from apps.email_service.signals import send_email_signal

# Send a user registration email
send_email_signal.send(
    sender=User,
    action='user_registered',
    recipient=user.email,
    user=user,
    context={
        'verification_url': 'https://yourapp.com/verify?token=xyz'
    }
)
```

#### Available Built-in Actions

```python
# User registered - sends verification email
send_email_signal.send(
    sender=User,
    action='user_registered',
    recipient=user.email,
    user=user,
    context={'verification_url': 'https://...'}
)

# Password reset requested
send_email_signal.send(
    sender=User,
    action='password_reset',
    recipient=user.email,
    user=user,
    context={'reset_url': 'https://...'}
)

# Email verified - sends welcome email
send_email_signal.send(
    sender=User,
    action='email_verified',
    recipient=user.email,
    user=user
)

# Password changed
send_email_signal.send(
    sender=User,
    action='password_changed',
    recipient=user.email,
    user=user
)
```

#### Custom Email with Signal

```python
send_email_signal.send(
    sender=YourModel,
    action='custom',
    recipient='user@example.com',
    user=user,  # optional
    template_name='emails/custom_email.html',  # required for custom
    subject='Your Custom Email',  # required for custom
    context={
        'custom_field': 'value',
        'another_field': 'data'
    }
)
```

### 2. Direct Email Service Usage

For more control, use `EmailService` directly:

```python
from apps.email_service.services import EmailService

# Send template email
EmailService.send_template_email(
    to_email='user@example.com',
    template_name='emails/welcome.html',
    context={'user': user, 'custom_data': 'value'},
    subject='Welcome!'
)

# Send raw HTML email
EmailService.send_email(
    to_email='user@example.com',
    subject='Hello',
    html_content='<h1>Hello World</h1>'
)
```

---

## Creating Email Templates

### Option 1: Database Templates (Admin Panel)

1. Go to Django admin: `/admin/email_service/emailtemplate/`
2. Click "Add Email Template"
3. Fill in:
   - **Name**: Template identifier (e.g., `user_registered`)
   - **Subject**: Email subject (supports `{{variables}}`)
   - **HTML Content**: Email body (supports `{{variables}}`)
   - **Description**: What this template is for

**Example Template:**

```html
<!-- Subject -->
Welcome to {{site_name}}, {{user.first_name}}!

<!-- HTML Content -->
<!DOCTYPE html>
<html>
<body>
    <h1>Welcome, {{user.first_name}}!</h1>
    <p>Thank you for joining {{site_name}}.</p>
    <a href="{{verification_url}}">Verify your email</a>
</body>
</html>
```

### Option 2: Static File Templates

Create template files in `apps/email_service/templates/emails/`:

```html
<!-- apps/email_service/templates/emails/custom_email.html -->
<!DOCTYPE html>
<html>
<body>
    <h1>Hello, {{ user.first_name }}!</h1>
    <p>{{ custom_message }}</p>
</body>
</html>
```

---

## Adding New Email Actions

### 1. Define Action in Signals

Edit `apps/email_service/signals.py`:

```python
def get_email_config_for_action(action: str) -> dict:
    configs = {
        # ... existing actions ...

        'order_confirmed': {
            'template_name': 'emails/order_confirmed.html',
            'subject': 'Your order is confirmed!',
            'enabled': True,
        },
    }
    return configs.get(action, {...})
```

### 2. Create Template

Create the template (database or static file):

```html
<!-- emails/order_confirmed.html -->
<h1>Order Confirmed!</h1>
<p>Hi {{user.first_name}},</p>
<p>Your order #{{order.id}} has been confirmed.</p>
```

### 3. Trigger the Signal

```python
from apps.email_service.signals import send_email_signal

send_email_signal.send(
    sender=Order,
    action='order_confirmed',
    recipient=user.email,
    user=user,
    context={'order': order}
)
```

---

## Email Logging

All emails are automatically logged to the database. View logs at:

- **Admin Panel**: `/admin/email_service/emaillog/`
- **Programmatically**:

```python
from apps.email_service.models import EmailLog

# Get recent emails
recent_emails = EmailLog.objects.all()[:10]

# Get failed emails
failed_emails = EmailLog.objects.filter(status='failed')

# Get emails for a specific user
user_emails = EmailLog.objects.filter(to_email=user.email)
```

---

## Provider Configuration

### SMTP (Default)

```env
EMAIL_PROVIDER=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### SendGrid

```env
EMAIL_PROVIDER=sendgrid
EMAIL_PROVIDER_API_KEY=SG.your-api-key
```

### Resend

```env
EMAIL_PROVIDER=resend
EMAIL_PROVIDER_API_KEY=re_your-api-key
```

---

## Development Tips

### Disable Emails in Development

```env
EMAIL_ENABLED=False
```

### Use Console Backend for Testing

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Use Static Templates Only

```env
USE_DB_EMAIL_TEMPLATES=static
```

---

## Context Variables

These variables are automatically available in all email templates:

- `user` - User object (if provided)
- `site_name` - From `SITE_NAME` setting
- `frontend_url` - From `FRONTEND_URL` setting

Plus any custom context you provide when triggering the signal.

---

## Example: Complete Flow

```python
# 1. User registers
user = User.objects.create_user(email='user@example.com', ...)

# 2. Create verification token
token = create_verification_token(user)

# 3. Send email via signal
from apps.email_service.signals import send_email_signal

send_email_signal.send(
    sender=User,
    action='user_registered',
    recipient=user.email,
    user=user,
    context={
        'verification_url': f'https://yourapp.com/verify?token={token}'
    }
)

# Email is automatically sent and logged!
```

---

## Troubleshooting

### Emails not sending?

1. Check `EMAIL_ENABLED=True` in `.env`
2. Verify email provider credentials
3. Check logs: `EmailLog.objects.filter(status='failed')`

### Template not found?

1. Verify `USE_DB_EMAIL_TEMPLATES` setting
2. Check template exists in database or static files
3. Ensure template name matches exactly

### Wrong provider?

Check `EMAIL_PROVIDER` in `.env` matches your configuration.

---

## API Reference

### EmailService Methods

- `send_email(to_email, subject, html_content, **kwargs)`
- `send_template_email(to_email, template_name, context, subject, **kwargs)`
- `send_verification_email(user, token)`
- `send_password_reset_email(user, token)`
- `send_welcome_email(user)`

### Signal Parameters

- `sender` - Model class that sent the signal
- `action` - Action name (string)
- `recipient` - Recipient email address
- `user` - User object (optional)
- `context` - Template context dict
- `template_name` - Override template (optional)
- `subject` - Override subject (optional)
