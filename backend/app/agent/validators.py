"""Validators for Singapore SMB Support Agent responses."""

from enum import Enum

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    """Sentiment analysis results."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"


class PDPACompliance(BaseModel):
    """PDPA compliance check results."""

    is_compliant: bool
    violations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Complete validation result."""

    is_valid: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    sentiment: Sentiment
    pdpa_compliance: PDPACompliance
    requires_escalation: bool
    requires_followup: bool
    message: str | None = None


class ResponseValidator:
    """Validate agent responses for quality, sentiment, and compliance."""

    @staticmethod
    def validate_confidence(confidence: float, threshold: float = 0.5) -> bool:
        """
        Validate confidence score.

        Args:
            confidence: Confidence score (0.0 to 1.0)
            threshold: Minimum acceptable threshold

        Returns:
            True if confidence meets threshold
        """
        return confidence >= threshold

    @staticmethod
    def analyze_sentiment(text: str) -> Sentiment:
        """
        Simple sentiment analysis based on keyword matching.

        Args:
            text: Text to analyze

        Returns:
            Sentiment enum value
        """
        negative_keywords = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "disappointed",
            "unhappy",
            "poor",
            "angry",
            "frustrated",
            "annoyed",
            "upset",
        ]

        frustrated_keywords = [
            "stupid",
            "ridiculous",
            "impossible",
            "useless",
            "waste",
            "never",
            "again",
        ]

        positive_keywords = [
            "good",
            "great",
            "excellent",
            "love",
            "happy",
            "pleased",
            "satisfied",
            "helpful",
            "thank",
            "appreciate",
        ]

        text_lower = text.lower()

        frustrated_count = sum(1 for kw in frustrated_keywords if kw in text_lower)
        if frustrated_count >= 2:
            return Sentiment.FRUSTRATED

        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        if negative_count >= 2:
            return Sentiment.NEGATIVE

        angry_keywords = ["angry", "furious", "rage", "livid"]
        if any(kw in text_lower for kw in angry_keywords):
            return Sentiment.ANGRY

        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        if positive_count >= 1:
            return Sentiment.POSITIVE

        return Sentiment.NEUTRAL

    @staticmethod
    def check_pdpa_compliance(
        text: str, context: dict | None = None
    ) -> PDPACompliance:
        """
        Check PDPA compliance for response.

        Args:
            text: Response text to check
            context: Additional context (customer info, etc.)

        Returns:
            PDPACompliance with violations and warnings
        """
        violations = []
        warnings = []

        personal_info_patterns = [
            "NRIC",
            "passport",
            "credit card",
            "bank account",
            "medical",
            "health condition",
        ]

        text_lower = text.lower()

        for pattern in personal_info_patterns:
            if pattern in text_lower:
                warnings.append(f"Potential personal data mentioned: {pattern}")

        sharing_patterns = [
            "share with",
            "send to",
            "give to",
            "provide to",
            "third party",
            "external",
        ]

        if any(pattern in text_lower for pattern in sharing_patterns):
            violations.append("Unauthorized data sharing detected")

        context_patterns = [
            "based on your account",
            "from your profile",
            "your data shows",
            "your records indicate",
        ]

        if any(pattern in text_lower for pattern in context_patterns):
            warnings.append(
                "Customer-specific data referenced without explicit access request"
            )

        is_compliant = len(violations) == 0

        return PDPACompliance(
            is_compliant=is_compliant,
            violations=violations,
            warnings=warnings,
        )

    @classmethod
    def validate_response(
        cls,
        text: str,
        confidence: float = 0.7,
        context: dict | None = None,
        confidence_threshold: float = 0.5,
    ) -> ValidationResult:
        """
        Comprehensive validation of agent response.

        Args:
            text: Response text
            confidence: Confidence score
            context: Additional context
            confidence_threshold: Minimum confidence threshold

        Returns:
            ValidationResult with all validation checks
        """
        sentiment = cls.analyze_sentiment(text)
        pdpa_compliance = cls.check_pdpa_compliance(text, context)

        confidence_valid = cls.validate_confidence(confidence, confidence_threshold)
        is_valid = confidence_valid and pdpa_compliance.is_compliant

        requires_escalation = (
            sentiment in [Sentiment.ANGRY, Sentiment.FRUSTRATED]
            or not pdpa_compliance.is_compliant
        )

        requires_followup = sentiment == Sentiment.NEGATIVE or confidence < 0.7

        message_parts = []
        if not confidence_valid:
            message_parts.append("Low confidence response")
        if not pdpa_compliance.is_compliant:
            message_parts.append("PDPA compliance issues detected")
        if requires_escalation:
            message_parts.append("Escalation recommended")

        message = "; ".join(message_parts) if message_parts else None

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            sentiment=sentiment,
            pdpa_compliance=pdpa_compliance,
            requires_escalation=requires_escalation,
            requires_followup=requires_followup,
            message=message,
        )

    @staticmethod
    def sanitize_response(text: str) -> str:
        """
        Sanitize response to remove potential PDPA violations.

        Args:
            text: Response text to sanitize

        Returns:
            Sanitized text
        """
        from re import sub

        sensitive_patterns = [
            (r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "[CREDIT_CARD]"),
            (r"\b[A-Z]\d{7}[A-Z]\b", "[NRIC]"),
            (r"\b\d{9}\b", "[PHONE]"),
        ]

        sanitized = text
        for pattern, replacement in sensitive_patterns:
            sanitized = sub(pattern, replacement, sanitized)

        return sanitized
