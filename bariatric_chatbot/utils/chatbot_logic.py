import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ChatbotLogic:
    def __init__(self):
        self.surgery_types = {
            'gastric_bypass': {
                'name': 'Gastric Bypass Surgery',
                'description': 'A surgical procedure that creates a small pouch from the stomach and connects it directly to the small intestine.',
                'cost_range': {'min': 20000, 'max': 25000},
                'requirements': [
                    'BMI ≥ 40, or BMI ≥ 35 with obesity-related conditions',
                    'Age 18-65',
                    'Previous failed weight loss attempts',
                    'Psychological evaluation',
                    'Medical clearance'
                ],
                'risks': [
                    'Infection',
                    'Blood clots',
                    'Leaking at surgical connections',
                    'Malnutrition',
                    'Dumping syndrome'
                ]
            },
            'sleeve_gastrectomy': {
                'name': 'Sleeve Gastrectomy',
                'description': 'A surgical weight-loss procedure that removes about 80% of the stomach.',
                'cost_range': {'min': 15000, 'max': 20000},
                'requirements': [
                    'BMI ≥ 40, or BMI ≥ 35 with obesity-related conditions',
                    'Age 18-65',
                    'Commitment to lifestyle changes',
                    'Psychological evaluation',
                    'Medical clearance'
                ],
                'risks': [
                    'Infection',
                    'Bleeding',
                    'Blood clots',
                    'Leaking from the cut edge of the stomach',
                    'Acid reflux'
                ]
            }
        }
        
        self.diet_phases = {
            'pre_op': {
                'duration': '2 weeks before surgery',
                'allowed_foods': [
                    'Clear liquids',
                    'Sugar-free beverages',
                    'Protein shakes',
                    'Broth'
                ],
                'restricted_foods': [
                    'Solid foods',
                    'Sugary drinks',
                    'Alcoholic beverages',
                    'Caffeine'
                ]
            },
            'post_op_phase1': {
                'duration': '1-2 weeks after surgery',
                'allowed_foods': [
                    'Clear liquids',
                    'Water',
                    'Sugar-free beverages',
                    'Broth'
                ],
                'restricted_foods': [
                    'All solid foods',
                    'Sugary drinks',
                    'Carbonated beverages'
                ]
            },
            'post_op_phase2': {
                'duration': '2-4 weeks after surgery',
                'allowed_foods': [
                    'Protein shakes',
                    'Smooth pureed foods',
                    'Sugar-free yogurt',
                    'Cream soups'
                ],
                'restricted_foods': [
                    'Solid foods',
                    'Raw vegetables',
                    'Bread',
                    'Rice'
                ]
            }
        }

    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process the user message and return an appropriate response
        """
        try:
            message = message.lower().strip()
            
            # Check for greetings
            if self._is_greeting(message):
                return {
                    'message': 'Hello! I\'m your bariatric surgery assistant. I can help you with information about:\n'
                              '1. Types of bariatric surgery\n'
                              '2. Cost and requirements\n'
                              '3. Pre and post-operative procedures\n'
                              '4. Diet plans\n'
                              '5. Eligibility check\n'
                              '6. Appointment scheduling\n'
                              'What would you like to know about?',
                    'intent': 'greeting',
                    'confidence': 1.0
                }

            # Check for surgery type inquiries
            if self._is_surgery_type_query(message):
                return self._get_surgery_info(message)

            # Check for cost inquiries
            if self._is_cost_query(message):
                return self._get_cost_info(message)

            # Check for requirements/eligibility
            if self._is_requirements_query(message):
                return self._get_requirements_info(message)

            # Check for diet plan inquiries
            if self._is_diet_query(message):
                return self._get_diet_info(message)

            # Check for appointment related queries
            if self._is_appointment_query(message):
                return self._get_appointment_info(message)

            # Check for risks/complications queries
            if self._is_risks_query(message):
                return self._get_risks_info(message)

            # Default response for unrecognized queries
            return {
                'message': 'I\'m not sure I understand. Could you please rephrase your question? '
                          'You can ask about surgery types, costs, requirements, diet plans, or scheduling appointments.',
                'intent': 'unknown',
                'confidence': 0.0
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'message': 'I apologize, but I encountered an error processing your request. '
                          'Please try again or contact our support team.',
                'intent': 'error',
                'confidence': 0.0
            }

    def _is_greeting(self, message: str) -> bool:
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'start']
        return any(greeting in message for greeting in greetings)

    def _is_surgery_type_query(self, message: str) -> bool:
        keywords = ['surgery', 'surgeries', 'procedure', 'bypass', 'sleeve', 'types', 'options']
        return any(keyword in message for keyword in keywords)

    def _is_cost_query(self, message: str) -> bool:
        keywords = ['cost', 'price', 'expensive', 'payment', 'insurance', 'afford']
        return any(keyword in message for keyword in keywords)

    def _is_requirements_query(self, message: str) -> bool:
        keywords = ['requirement', 'qualify', 'eligible', 'eligibility', 'qualify', 'bmi']
        return any(keyword in message for keyword in keywords)

    def _is_diet_query(self, message: str) -> bool:
        keywords = ['diet', 'eat', 'food', 'nutrition', 'meal', 'eating']
        return any(keyword in message for keyword in keywords)

    def _is_appointment_query(self, message: str) -> bool:
        keywords = ['appointment', 'schedule', 'book', 'visit', 'consult', 'meet']
        return any(keyword in message for keyword in keywords)

    def _is_risks_query(self, message: str) -> bool:
        keywords = ['risk', 'complication', 'danger', 'safe', 'side effect']
        return any(keyword in message for keyword in keywords)

    def _get_surgery_info(self, message: str) -> Dict[str, Any]:
        response = "Here are the main types of bariatric surgery we offer:\n\n"
        
        for surgery_type, info in self.surgery_types.items():
            response += f"📍 {info['name']}:\n"
            response += f"   {info['description']}\n\n"
        
        response += "Would you like to know more about a specific type of surgery?"
        
        return {
            'message': response,
            'intent': 'surgery_info',
            'confidence': 0.9
        }

    def _get_cost_info(self, message: str) -> Dict[str, Any]:
        response = "Here are the typical cost ranges for different bariatric procedures:\n\n"
        
        for surgery_type, info in self.surgery_types.items():
            response += f"📍 {info['name']}:\n"
            response += f"   ${info['cost_range']['min']:,} - ${info['cost_range']['max']:,}\n\n"
        
        response += ("Note: Final costs may vary based on your specific case, location, and insurance coverage. "
                    "Would you like to discuss financing options or insurance coverage?")
        
        return {
            'message': response,
            'intent': 'cost_info',
            'confidence': 0.9
        }

    def _get_requirements_info(self, message: str) -> Dict[str, Any]:
        response = "General requirements for bariatric surgery include:\n\n"
        
        # Using the first surgery type's requirements as they're generally similar
        requirements = self.surgery_types['gastric_bypass']['requirements']
        
        for req in requirements:
            response += f"✓ {req}\n"
        
        response += "\nWould you like to schedule an evaluation to check your eligibility?"
        
        return {
            'message': response,
            'intent': 'requirements_info',
            'confidence': 0.9
        }

    def _get_diet_info(self, message: str) -> Dict[str, Any]:
        response = "Here's an overview of the diet phases:\n\n"
        
        for phase, info in self.diet_phases.items():
            phase_name = phase.replace('_', ' ').title()
            response += f"📍 {phase_name} ({info['duration']}):\n"
            response += "   Allowed foods:\n"
            for food in info['allowed_foods']:
                response += f"   ✓ {food}\n"
            response += "   Restricted foods:\n"
            for food in info['restricted_foods']:
                response += f"   ⛔ {food}\n"
            response += "\n"
        
        response += "Would you like more specific information about any phase?"
        
        return {
            'message': response,
            'intent': 'diet_info',
            'confidence': 0.9
        }

    def _get_appointment_info(self, message: str) -> Dict[str, Any]:
        response = ("To schedule an appointment, we'll need the following information:\n\n"
                   "1. Your basic information (name, contact details)\n"
                   "2. Preferred appointment dates and times\n"
                   "3. Type of appointment (initial consultation, follow-up, etc.)\n"
                   "4. Any specific concerns you'd like to discuss\n\n"
                   "Would you like to proceed with scheduling an appointment?")
        
        return {
            'message': response,
            'intent': 'appointment_info',
            'confidence': 0.9
        }

    def _get_risks_info(self, message: str) -> Dict[str, Any]:
        response = "Here are the potential risks and complications for different procedures:\n\n"
        
        for surgery_type, info in self.surgery_types.items():
            response += f"📍 {info['name']}:\n"
            for risk in info['risks']:
                response += f"   ⚠ {risk}\n"
            response += "\n"
        
        response += ("Remember that our team takes every precaution to minimize these risks. "
                    "Would you like to discuss these in detail with a healthcare provider?")
        
        return {
            'message': response,
            'intent': 'risks_info',
            'confidence': 0.9
        }

# Initialize the chatbot
chatbot = ChatbotLogic()

def process_message(message: str) -> Dict[str, Any]:
    """
    Process a message using the chatbot logic
    """
    return chatbot.process_message(message)
