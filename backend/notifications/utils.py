from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from twilio.rest import Client
import firebase_admin
from firebase_admin import messaging
from .models import Notification
import asyncio

def send_notification(user, type, title, message, link=''):
    notification = Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        link=link
    )
    
    preferences = user.notification_preferences.first()
    if not preferences:
        return notification
    
    if preferences.email_notifications and user.email:
        send_email_notification(user.email, title, message)
    
    if preferences.sms_notifications and user.phone:
        send_sms_notification(user.phone, message)
    
    if preferences.push_notifications:
        send_user_push_notification(user, title, message)
    
    asyncio.run(send_websocket_notification(user.id, {
        "title": title,
        "message": message,
        "link": link
    }))
    
    return notification

def send_email_notification(email, subject, message):
    try:
        html_message = render_to_string('notifications/email_template.html', {
            'title': subject,
            'message': message,
            'site_url': settings.SITE_URL
        })
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_sms_notification(phone_number, message):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def send_user_push_notification(user, title, message):
    if not user.fcm_token:
        return False
        
    try:
        if not firebase_admin._apps:
            cred = firebase_admin.credentials.Certificate(settings.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred)
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            token=user.fcm_token,
            data={
                'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                'type': 'notification'
            }
        )
        
        response = messaging.send(message)
        return True
    except Exception as e:
        print(f"Error sending push notification: {str(e)}")
        return False

def send_push_notification(subscription, title, message):
    try:
        if not firebase_admin._apps:
            cred = firebase_admin.credentials.Certificate(settings.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred)
            
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            token=subscription,
        )
        
        response = messaging.send(message)
        return True
    except Exception as e:
        print(f"Error sending push notification: {str(e)}")
        return False

async def send_websocket_notification(user_id, notification_data):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    room_group_name = f"user_{user_id}_notifications"
    
    await channel_layer.group_send(
        room_group_name,
        {
            "type": "notification_message",
            "message": notification_data
        }
    )

def send_bulk_notification(users, type, title, message, link=''):
    notifications = []
    for user in users:
        notification = send_notification(user, type, title, message, link)
        notifications.append(notification)
    return notifications
