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
