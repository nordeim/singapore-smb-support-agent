"""Response templates for Singapore SMB Support Agent."""

from typing import Optional


class ResponseTemplates:
    """Pre-defined response templates for common scenarios."""

    @staticmethod
    def greeting() -> str:
        return "Hello! Welcome to our support service. How can I help you today?"

    @staticmethod
    def goodbye() -> str:
        return "Thank you for contacting us. Have a great day ahead!"

    @staticmethod
    def acknowledge(query: str) -> str:
        return f"I understand you're asking about {query}. Let me help you with that."

    @staticmethod
    def clarification_needed() -> str:
        return "I'd like to help you better. Could you provide more details about your inquiry?"

    @staticmethod
    def no_information_found(topic: str) -> str:
        return f"I couldn't find specific information about {topic} in my knowledge base. Would you like me to connect you with a human agent?"

    @staticmethod
    def business_hours() -> str:
        return "Our business hours are 9:00 AM to 6:00 PM, Monday to Friday (Singapore Time). We're closed on weekends and public holidays."

    @staticmethod
    def out_of_business_hours() -> str:
        return "We're currently outside business hours. Please leave your inquiry and we'll get back to you by the next business day."

    @staticmethod
    def escalation_initiated() -> str:
        return "I'm connecting you with a human agent now. Please hold while I transfer your conversation."

    @staticmethod
    def escalation_ticket_created(ticket_id: str) -> str:
        return f"I've created a support ticket for you (ID: {ticket_id}). Our team will review and respond within 24 hours during business hours."

    @staticmethod
    def follow_up_confirmation() -> str:
        return "Is there anything else I can help you with today?"

    @staticmethod
    def apology() -> str:
        return "I apologize for the inconvenience. Let me help resolve this for you."

    @staticmethod
    def thank_you() -> str:
        return "Thank you for your patience. I'm glad I could help!"

    @staticmethod
    def customer_info_found(name: Optional[str] = None) -> str:
        if name:
            return f"I found your account, {name}. How can I assist you today?"
        return "I found your account. How can I assist you today?"

    @staticmethod
    def customer_info_not_found(identifier: str) -> str:
        return f"I couldn't find an account matching {identifier}. Please verify the information or contact our support team."

    @staticmethod
    def action_in_progress(action: str) -> str:
        return f"I'm {action} for you now. This may take a moment..."

    @staticmethod
    def action_completed(action: str) -> str:
        return f"I've successfully {action}. Is there anything else you need?"

    @staticmethod
    def general_help() -> str:
        return """I can help you with:

• Product information and features
• Account and billing inquiries
• Technical support and troubleshooting
• Business hours and scheduling
• General questions about our services

Just ask me anything, and I'll do my best to assist you!"""

    @staticmethod
    def privacy_assurance() -> str:
        return "Your privacy is important to us. I'll only access your information when necessary to assist with your inquiry."

    @staticmethod
    def slow_response() -> str:
        return "I'm taking a bit longer than expected to find the information. Thank you for your patience."

    @staticmethod
    def technical_difficulty() -> str:
        return "I'm experiencing some technical difficulty. Let me connect you with a human agent who can help."

    @staticmethod
    def singapore_holiday_reminder() -> str:
        return "Please note that we're closed on Singapore public holidays. Our team will respond on the next business day."

    @staticmethod
    def low_confidence_response() -> str:
        return "I want to make sure I give you accurate information. Let me connect you with a human agent who can better assist with this inquiry."

    @staticmethod
    def complex_issue() -> str:
        return "This is a complex matter that requires careful attention. I'm connecting you with a specialist who can help you better."

    @staticmethod
    def payment_security() -> str:
        return "For your security, I cannot access or modify payment details directly. Let me connect you with our secure payment support team."

    @staticmethod
    def account_security() -> str:
        return "For account security purposes, I can only provide limited account information. A human agent will need to verify your identity for detailed account access."

    @staticmethod
    def callback_requested() -> str:
        return "I've scheduled a callback for you. Our team will call you at the requested time within business hours."

    @staticmethod
    def email_confirmation(topic: str) -> str:
        return f"I've sent you an email with details about {topic}. Please check your inbox."

    @staticmethod
    def maintenance_notice() -> str:
        return "We're currently performing scheduled maintenance. Some services may be temporarily unavailable. We apologize for the inconvenience."

    @staticmethod
    def feature_not_available(feature: str) -> str:
        return f"{feature} is not currently available. Let me connect you with a human agent to discuss alternatives or timeline."


def get_template(name: str, **kwargs) -> Optional[str]:
    """Get a response template by name."""
    template_method = getattr(ResponseTemplates, name, None)
    if template_method and callable(template_method):
        result = template_method(**kwargs)
        return str(result) if result is not None else None
    return None
