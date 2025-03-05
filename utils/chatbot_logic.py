import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ChatbotLogic:
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process incoming chat messages and return appropriate responses."""
        try:
            # Basic intent detection
            message = message.lower()
            
            if any(word in message for word in ['hello', 'hi', 'hey']):
                return {
                    'message': 'Hello! How can I help you with your bariatric surgery questions today?',
                    'intent': 'greeting',
                    'confidence': 0.9
                }
            
            if any(word in message for word in ['surgery', 'procedure', 'operation']):
                return {
                    'message': 'We offer several types of bariatric surgery including gastric bypass, sleeve gastrectomy, and adjustable gastric banding. Would you like to learn more about a specific procedure?',
                    'intent': 'surgery_info',
                    'confidence': 0.8
                }
            
            if any(word in message for word in ['appointment', 'schedule', 'book']):
                return {
                    'message': 'I can help you schedule an appointment. Please provide your preferred date and time, or I can show you our available slots.',
                    'intent': 'appointment',
                    'confidence': 0.8
                }
            
            if any(word in message for word in ['cost', 'price', 'expensive', 'insurance']):
                return {
                    'message': 'The cost of bariatric surgery varies depending on the procedure and insurance coverage. Would you like to discuss specific procedures or insurance options?',
                    'intent': 'cost_info',
                    'confidence': 0.8
                }
            
            # Default response for unrecognized queries
            return {
                'message': 'I can help you with information about bariatric surgery procedures, scheduling appointments, costs, and post-operative care. What would you like to know more about?',
                'intent': 'general',
                'confidence': 0.6
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

# Initialize the chatbot
chatbot = ChatbotLogic()

def process_message(message: str) -> Dict[str, Any]:
    """
    Process a message using the chatbot logic
    """
    return chatbot.process_message(message)
