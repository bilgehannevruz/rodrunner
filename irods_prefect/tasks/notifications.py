"""
Notification tasks for Prefect workflows.
"""
from typing import Dict, List, Optional, Union, Any
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from prefect import task

from irods_prefect.models.config import NotificationConfig


@task(name="send_email_notification")
def send_email_notification(
    config: NotificationConfig,
    subject: str,
    message: str,
    recipients: Optional[List[str]] = None
) -> bool:
    """
    Send an email notification.
    
    Args:
        config: Notification configuration
        subject: Email subject
        message: Email message
        recipients: List of recipient email addresses (defaults to config.email_to)
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    if not config.email_enabled:
        return False
    
    if not config.email_smtp_server or not config.email_smtp_port:
        return False
    
    if not config.email_from:
        return False
    
    to_emails = recipients or config.email_to
    if not to_emails:
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.email_from
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        
        # Add message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(config.email_smtp_server, config.email_smtp_port)
        server.starttls()
        
        # Login if credentials are provided
        if config.email_username and config.email_password:
            server.login(config.email_username, config.email_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


@task(name="send_slack_notification")
def send_slack_notification(
    config: NotificationConfig,
    message: str,
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send a Slack notification.
    
    Args:
        config: Notification configuration
        message: Slack message
        webhook_url: Slack webhook URL (defaults to config.slack_webhook_url)
        
    Returns:
        True if the notification was sent successfully, False otherwise
    """
    if not config.slack_enabled:
        return False
    
    url = webhook_url or config.slack_webhook_url
    if not url:
        return False
    
    try:
        payload = {
            "text": message
        }
        
        response = requests.post(url, json=payload)
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Slack notification: {str(e)}")
        return False


@task(name="send_workflow_success_notification")
def send_workflow_success_notification(
    config: NotificationConfig,
    workflow_name: str,
    run_id: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Send a notification for a successful workflow run.
    
    Args:
        config: Notification configuration
        workflow_name: Name of the workflow
        run_id: Run ID
        details: Additional details about the workflow run
    """
    subject = f"Workflow Success: {workflow_name}"
    
    message = f"Workflow '{workflow_name}' completed successfully.\n\n"
    message += f"Run ID: {run_id}\n"
    
    if details:
        message += "\nDetails:\n"
        for key, value in details.items():
            message += f"{key}: {value}\n"
    
    # Send email notification
    if config.email_enabled:
        send_email_notification(config, subject, message)
    
    # Send Slack notification
    if config.slack_enabled:
        slack_message = f"*Workflow Success: {workflow_name}*\n"
        slack_message += f"Run ID: {run_id}\n"
        
        if details:
            slack_message += "\nDetails:\n"
            for key, value in details.items():
                slack_message += f"• {key}: {value}\n"
        
        send_slack_notification(config, slack_message)


@task(name="send_workflow_failure_notification")
def send_workflow_failure_notification(
    config: NotificationConfig,
    workflow_name: str,
    run_id: str,
    error: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Send a notification for a failed workflow run.
    
    Args:
        config: Notification configuration
        workflow_name: Name of the workflow
        run_id: Run ID
        error: Error message
        details: Additional details about the workflow run
    """
    subject = f"Workflow Failure: {workflow_name}"
    
    message = f"Workflow '{workflow_name}' failed.\n\n"
    message += f"Run ID: {run_id}\n"
    message += f"Error: {error}\n"
    
    if details:
        message += "\nDetails:\n"
        for key, value in details.items():
            message += f"{key}: {value}\n"
    
    # Send email notification
    if config.email_enabled:
        send_email_notification(config, subject, message)
    
    # Send Slack notification
    if config.slack_enabled:
        slack_message = f"*Workflow Failure: {workflow_name}*\n"
        slack_message += f"Run ID: {run_id}\n"
        slack_message += f"Error: {error}\n"
        
        if details:
            slack_message += "\nDetails:\n"
            for key, value in details.items():
                slack_message += f"• {key}: {value}\n"
        
        send_slack_notification(config, slack_message)
