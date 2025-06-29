import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.shortcuts import render

from .models import SocialPost
from script.all_social import send_file_to_discord, post_to_facebook, send_media_to_telegram

@csrf_exempt
def social_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        content = request.POST.get('content', '')
        
        # Check if we have a file (photo or video)
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'A photo or video file is required'}, status=400)
        
        media_file = request.FILES['file']
        file_path = default_storage.save(f'tmp/{media_file.name}', ContentFile(media_file.read()))
        file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Determine if the file is a video based on its extension
        is_video = media_file.name.lower().endswith(('.mp4', '.mov', '.avi', '.wmv'))
        
        # List of all platforms to post to
        platforms = ['FACEBOOK', 'TELEGRAM', 'DISCORD']
        post_results = []
        
        for platform in platforms:
            # Create a record in the database
            social_post = SocialPost(
                platform=platform,
                content=content,
                photo=None if is_video else media_file,
                video=media_file if is_video else None,
                status='PROCESSING'
            )
            social_post.save()
            
            # Post to the platform
            try:
                if platform == 'DISCORD':
                    send_file_to_discord(file_path, content)
                elif platform == 'FACEBOOK':
                    post_to_facebook(file_path, content, is_video)
                elif platform == 'TELEGRAM':
                    send_media_to_telegram(file_path, content, is_video)
                
                # Update status to success
                social_post.status = 'POSTED'
                social_post.save()
                post_results.append({'platform': platform, 'status': 'success'})
            except Exception as e:
                # Update status to failed
                social_post.status = 'FAILED'
                social_post.save()
                post_results.append({'platform': platform, 'status': 'failed', 'error': str(e)})
        
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return JsonResponse({'message': 'Posted to all social media platforms', 'results': post_results})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def post_emergency_to_social_media(emergency_data, location_data=None, media_file=None):
    """
    Post emergency report to all social media platforms
    
    Args:
        emergency_data: Emergency report data (description, type, etc.)
        location_data: Location data of the emergency (optional)
        media_file: Image or video file to be attached to the post (optional)
    
    Returns:
        dict: Results of posting to each platform
    """
    try:
        # Prepare content for social media post
        description = emergency_data.get('description', 'Emergency reported')
        emergency_type = emergency_data.get('emergency_type', 'GENERAL')
        
        # Extract additional emergency details
        contact_info = emergency_data.get('contact_info', '')
        severity = emergency_data.get('severity', '')
        people_count = emergency_data.get('people_count', '')
        
        # Create more descriptive content for social media
        location_info = ""
        if location_data:
            if location_data.get('address'):
                location_info = f"📍 Location: {location_data.get('address')}"
            elif location_data.get('latitude') and location_data.get('longitude'):
                location_info = f"📍 Location: Latitude {location_data.get('latitude')}, Longitude {location_data.get('longitude')}"
                # Add Google Maps link
                lat = location_data.get('latitude')
                lng = location_data.get('longitude')
                location_info += f"\n🗺️ Map: https://www.google.com/maps?q={lat},{lng}"
        
        # Build a more comprehensive message
        content = f"🚨 EMERGENCY ALERT 🚨\n\n{description}\n\n🔴 Type: {emergency_type}"
        
        if severity:
            content += f"\n⚠️ Severity: {severity}"
            
        if people_count:
            content += f"\n👥 People affected: {people_count}"
            
        if contact_info:
            content += f"\n📞 Contact: {contact_info}"
            
        if location_info:
            content += f"\n{location_info}"
            
        content += "\n\n#EmergencyAlert #ResQApp"
        
        # List of all platforms to post to
        platforms = ['FACEBOOK', 'TELEGRAM', 'DISCORD']
        post_results = []
        
        file_path = None
        is_video = False
        
        # Handle media file if provided
        if media_file:
            file_path = default_storage.save(f'tmp/{media_file.name}', ContentFile(media_file.read()))
            file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Determine if the file is a video based on its extension
            is_video = media_file.name.lower().endswith(('.mp4', '.mov', '.avi', '.wmv'))
        
        for platform in platforms:
            # Create a record in the database
            social_post = SocialPost(
                platform=platform,
                content=content,
                photo=None if not media_file or is_video else media_file,
                video=media_file if media_file and is_video else None,
                status='PROCESSING'
            )
            social_post.save()
            
            # Post to the platform
            try:
                if platform == 'DISCORD':
                    if file_path:
                        send_file_to_discord(file_path, content)
                    else:
                        send_file_to_discord(None, content)
                elif platform == 'FACEBOOK':
                    if file_path:
                        post_to_facebook(file_path, content, is_video)
                    else:
                        # Use Facebook Graph API to post text-only content
                        post_to_facebook(None, content, False)
                elif platform == 'TELEGRAM':
                    if file_path:
                        send_media_to_telegram(file_path, content, is_video)
                    else:
                        # Use Telegram API to send text-only message
                        send_media_to_telegram(None, content, False)
                
                # Update status to success
                social_post.status = 'POSTED'
                social_post.save()
                post_results.append({'platform': platform, 'status': 'success'})
            except Exception as e:
                # Update status to failed
                social_post.status = 'FAILED'
                social_post.save()
                post_results.append({'platform': platform, 'status': 'failed', 'error': str(e)})
        
        # Clean up the temporary file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        return {'success': True, 'results': post_results}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
