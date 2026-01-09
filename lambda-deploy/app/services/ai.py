from typing import Optional
from dataclasses import dataclass
import openai
from models.snort import SnortAlert
from config import get_settings

settings = get_settings()

@dataclass
class AlertAnalysis:
    analysis: str
    recommendations: Optional[str] = None
    confidence_score: float = 0.0

def analyze_alert(alert: SnortAlert, model: str = "gpt-4") -> AlertAnalysis:
    """
    Analyze a Snort alert using OpenAI's API.
    
    Args:
        alert: The SnortAlert object to analyze
        model: The OpenAI model to use for analysis
        
    Returns:
        AlertAnalysis object containing the analysis, recommendations, and confidence score
    """
    # Set up the OpenAI client
    openai.api_key = settings.openai_api_key
    
    # Construct the prompt
    prompt = f"""Analyze this Snort alert and provide:
1. A detailed analysis of what the alert means
2. Specific recommendations for addressing the issue
3. A confidence score (0-100) for your analysis

Alert Details:
- Type: {alert.alert_type}
- Priority: {alert.priority}
- Message: {alert.message}
- Source IP: {alert.source_ip}
- Destination IP: {alert.destination_ip}
- Protocol: {alert.protocol}
- Timestamp: {alert.timestamp}

Please format your response as follows:
ANALYSIS:
[Your detailed analysis here]

RECOMMENDATIONS:
[Your specific recommendations here]

CONFIDENCE: [0-100]
"""

    try:
        # Get the AI response
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Snort and network security expert. Provide clear, actionable analysis and recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Split the response into sections
        sections = content.split("\n\n")
        analysis = ""
        recommendations = ""
        confidence = 0.0
        
        for section in sections:
            if section.startswith("ANALYSIS:"):
                analysis = section.replace("ANALYSIS:", "").strip()
            elif section.startswith("RECOMMENDATIONS:"):
                recommendations = section.replace("RECOMMENDATIONS:", "").strip()
            elif section.startswith("CONFIDENCE:"):
                try:
                    confidence = float(section.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    confidence = 0.0
        
        return AlertAnalysis(
            analysis=analysis,
            recommendations=recommendations,
            confidence_score=confidence
        )
        
    except Exception as e:
        raise Exception(f"Error analyzing alert: {str(e)}") 