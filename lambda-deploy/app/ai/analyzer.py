import openai
from app.config import get_settings
from app.models.snort import SnortAlert, AlertAnalysis
from typing import List, Dict, Any
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class AlertAnalyzer:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.system_prompt = """You are an expert security analyst specializing in Snort IDS alerts. 
        Analyze the provided Snort alert and provide:
        1. A detailed analysis of the potential security implications
        2. Specific recommendations for addressing the issue
        3. A confidence score (0-1) for your analysis
        4. Any related patterns or context that might be relevant"""

    async def analyze_alert(self, alert: SnortAlert) -> AlertAnalysis:
        """Analyze a Snort alert using OpenAI"""
        try:
            prompt = f"""
            Alert Details:
            - Type: {alert.alert_type}
            - Priority: {alert.priority}
            - Protocol: {alert.protocol}
            - Source: {alert.source_ip}:{alert.source_port}
            - Destination: {alert.destination_ip}:{alert.destination_port}
            - Message: {alert.message}
            - Classification: {alert.classification}
            - Signature ID: {alert.signature_id}
            - Raw Alert: {alert.raw_alert}

            Please provide a detailed analysis of this alert.
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            analysis_text = response.choices[0].message.content

            # Extract recommendations and confidence score from the analysis
            recommendations = self._extract_recommendations(analysis_text)
            confidence_score = self._extract_confidence_score(analysis_text)

            return AlertAnalysis(
                alert=alert,
                analysis=analysis_text,
                recommendations=recommendations,
                confidence_score=confidence_score
            )

        except Exception as e:
            logger.error(f"Error analyzing alert with OpenAI: {str(e)}")
            return AlertAnalysis(
                alert=alert,
                analysis="Error analyzing alert",
                recommendations=["Check system logs for more details"],
                confidence_score=0.0
            )

    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from the analysis text"""
        # This is a simple implementation - you might want to make this more sophisticated
        recommendations = []
        for line in analysis_text.split('\n'):
            if line.strip().startswith(('-', '•', '*', '1.', '2.', '3.')):
                recommendations.append(line.strip().lstrip('-•*123456789. '))
        return recommendations if recommendations else ["No specific recommendations available"]

    def _extract_confidence_score(self, analysis_text: str) -> float:
        """Extract confidence score from the analysis text"""
        # This is a simple implementation - you might want to make this more sophisticated
        try:
            # Look for confidence score in the text
            if "confidence score:" in analysis_text.lower():
                score_text = analysis_text.lower().split("confidence score:")[1].split()[0]
                return float(score_text)
            return 0.5  # Default confidence score
        except:
            return 0.5  # Default confidence score if extraction fails 