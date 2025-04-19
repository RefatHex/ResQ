import logging
import requests
import json
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, messaging
from .models import Notification
from users.models import User

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK with the credentials provided
try:
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    firebase_initialized = True
    logger.info("Firebase successfully initialized")
except (ValueError, firebase_admin.exceptions.FirebaseError) as e:
    logger.error(f"Firebase initialization error: {str(e)}")
    firebase_initialized = False
except Exception as e:
    logger.error(f"Unexpected error initializing Firebase: {str(e)}")
    firebase_initialized = False

def send_push_notification(user_id, title, body, data=None):
    """
    Send a push notification to a user's device using FCM
    
    Args:
        user_id: ID of the user to send notification to
        title: Notification title
        body: Notification body text
        data: Optional data payload (dict)
    
    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Get user's FCM token
        user = User.objects.get(id=user_id)
        if not user.fcm_token:
            return False
        
        # Firebase Cloud Messaging API endpoint
        fcm_url = "https://fcm.googleapis.com/fcm/send"
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'key={settings.FIREBASE_CONFIG.get("serverKey", "")}'
        }
        
        # Prepare notification payload
        payload = {
            'to': user.fcm_token,
            'notification': {
                'title': title,
                'body': body,
                'sound': 'default',
                'badge': '1',
                'click_action': 'FLUTTER_NOTIFICATION_CLICK'
            }
        }
        
        # Add data payload if provided
        if data:
            payload['data'] = data
        
        # Send the notification
        response = requests.post(
            fcm_url, 
            headers=headers, 
            data=json.dumps(payload)
        )
        
        # Check response
        if response.status_code == 200:
            return True
        else:
            print(f"FCM notification failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending push notification: {str(e)}")
        return False

def send_topic_notification(topic, title, body, data=None):
    """
    Send notification to all users subscribed to a topic
    
    Args:
        topic: Topic name
        title: Notification title
        body: Notification body text
        data: Optional dictionary with additional data
        
    Returns:
        bool: Success status
    """
    if not firebase_initialized:
        logger.error("Firebase not initialized, can't send topic notification")
        return False
    
    try:
        # Create message for topic
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            topic=topic
        )
        
        # Send message
        response = messaging.send(message)
        logger.info(f"Successfully sent topic notification to {topic}: {response}")
        return True
        
    except messaging.exceptions.FirebaseError as e:
        logger.error(f"Firebase topic messaging error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending topic notification: {str(e)}")
        return False

def create_notification(user, title, message, notification_type='OTHER', send_push=True):
    """
    Create a notification in the database and optionally send push notification
    
    Args:
        user: User object or user_id to create notification for
        title: Notification title
        message: Notification content
        notification_type: Type of notification (from Notification.NOTIFICATION_TYPES)
        send_push: Whether to send a push notification
        
    Returns:
        Notification object or None if failed
    """
    try:
        # Handle if user_id was passed instead of user object
        if not isinstance(user, User):
            user = User.objects.get(id=user)
            
        # Create notification record
        notification = Notification.objects.create(
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
        
        # Send push notification if requested
        if send_push and user.fcm_token:
            data = {
                'notification_id': str(notification.id),
                'notification_type': notification_type
            }
            send_push_notification(
                user.id, 
                title, 
                message, 
                data=data
            )
            
        return notification
    except User.DoesNotExist:
        logger.error(f"User not found when creating notification")
        return None
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return None
