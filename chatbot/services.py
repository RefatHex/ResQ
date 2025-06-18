import google.generativeai as genai
from django.conf import settings
from typing import Dict, List, Optional
import json
from .models import ChatSession

class ChatbotService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Context prompt for emergency response system
        self.context_prompt = """
        You are ResQ AI, an intelligent assistant for an emergency response system. Your role is to:
        
        1. Help users understand emergency procedures and safety protocols
        2. Provide guidance on different types of emergencies (fire, medical, police, natural disasters)
        3. Assist with using the ResQ emergency response app features
        4. Give first aid and safety advice when appropriate
        5. Help users locate nearby emergency services
        
        IMPORTANT GUIDELINES:
        - Always prioritize user safety and encourage calling emergency services (911, local emergency numbers) for active emergencies
        - Provide clear, concise, and actionable advice
        - If unsure about medical advice, recommend consulting healthcare professionals
        - Stay within the scope of emergency response and safety topics
        - Be empathetic and supportive, especially during stressful situations
        - If asked about non-emergency topics, politely redirect to emergency/safety related assistance
        
        User roles in the system:
        - CITIZEN: Regular users who can report emergencies and seek help
        - FIRE_STATION: Fire department personnel
        - POLICE: Police officers
        - RED_CRESCENT: Medical emergency responders
        
        Current conversation context will be maintained throughout the session.
        """
    
    def get_user_sessions(self, user) -> List[Dict]:
        """Get recent chat sessions for context"""
        recent_sessions = ChatSession.objects.filter(
            user=user
        ).order_by('-timestamp')[:5]  # Last 5 messages for context
        
        return [
            {
                'role': 'user',
                'parts': [session.message]
            } if i % 2 == 0 else {
                'role': 'model', 
                'parts': [session.response]
            }
            for i, session in enumerate(reversed(recent_sessions))
        ]
    
    def generate_response(self, user, message: str) -> str:
        """Generate AI response with session context"""
        try:
            # Get conversation history for context
            history = self.get_user_sessions(user)
            
            # Start chat with context
            chat = self.model.start_chat(history=history)
            
            # Create user context based on role
            user_context = f"""
            User Information:
            - Role: {user.role}
            - Username: {user.username}
            
            User Message: {message}
            """
            
            # Generate response
            full_prompt = f"{self.context_prompt}\n\n{user_context}"
            response = chat.send_message(full_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error generating AI response: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now. For immediate emergencies, please call your local emergency services."
    
    def save_chat_session(self, user, message: str, response: str) -> ChatSession:
        """Save chat session to database"""
        return ChatSession.objects.create(
            user=user,
            message=message,
            response=response
        )
    
    def get_emergency_quick_responses(self) -> Dict[str, str]:
        """Get predefined quick responses for common emergency scenarios"""
        return {
            "fire": "🔥 FIRE EMERGENCY:\n1. Call emergency services immediately\n2. Evacuate the building safely\n3. Stay low to avoid smoke\n4. Don't use elevators\n5. Meet at designated assembly point",
            "medical": "🚑 MEDICAL EMERGENCY:\n1. Call emergency services (911)\n2. Check for responsiveness\n3. Check breathing and pulse\n4. Apply first aid if trained\n5. Stay with the person until help arrives",
            "police": "🚓 POLICE EMERGENCY:\n1. Call emergency services immediately\n2. Stay in a safe location\n3. Provide clear location details\n4. Follow dispatcher instructions\n5. Stay on the line until help arrives",
            "natural_disaster": "🌪️ NATURAL DISASTER:\n1. Follow local emergency broadcasts\n2. Take shelter immediately\n3. Stay away from windows\n4. Have emergency supplies ready\n5. Follow evacuation orders if given"
        }
