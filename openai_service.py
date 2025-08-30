import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def analyze_journal_sentiment(text):
    """
    Analyze the sentiment and emotions in a journal entry.
    Returns mood score (1-5), confidence (0-1), and detailed emotions.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": """You are a professional mental health sentiment analysis AI. 
                    Analyze the emotional content of journal entries with empathy and accuracy.
                    
                    Provide a mood score from 1-5 where:
                    1 = Very negative (depressed, hopeless, anxious)
                    2 = Negative (sad, worried, frustrated)
                    3 = Neutral (balanced, calm, neither positive nor negative)
                    4 = Positive (happy, content, optimistic)
                    5 = Very positive (joyful, excited, euphoric)
                    
                    Also provide a confidence score (0-1) and detailed emotion percentages.
                    Respond with JSON in this exact format:
                    {
                        "mood_score": number,
                        "confidence": number,
                        "emotions": {
                            "happiness": number,
                            "sadness": number,
                            "anxiety": number,
                            "anger": number,
                            "fear": number,
                            "excitement": number,
                            "calm": number,
                            "hope": number
                        }
                    }
                    """
                },
                {"role": "user", "content": f"Analyze this journal entry: {text}"}
            ],
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content or '{}')
        
        # Validate and normalize the results
        mood_score = max(1, min(5, round(result.get("mood_score", 3))))
        confidence = max(0, min(1, result.get("confidence", 0.5)))
        emotions = result.get("emotions", {})
        
        # Ensure all emotion values are between 0 and 100
        for emotion in emotions:
            emotions[emotion] = max(0, min(100, emotions[emotion]))
        
        return {
            "mood_score": mood_score,
            "confidence": confidence,
            "emotions": emotions
        }
        
    except Exception as e:
        # Return neutral values if analysis fails
        return {
            "mood_score": 3,
            "confidence": 0.0,
            "emotions": {
                "happiness": 0,
                "sadness": 0,
                "anxiety": 0,
                "anger": 0,
                "fear": 0,
                "excitement": 0,
                "calm": 50,
                "hope": 0
            },
            "error": str(e)
        }

def generate_mood_insights(entries_data):
    """
    Generate insights about mood patterns from multiple journal entries.
    """
    try:
        if not entries_data:
            return {"insights": "No entries available for analysis."}
            
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": """You are a mental health insights AI. Analyze mood patterns and provide 
                    helpful, encouraging insights about the user's emotional journey. Be supportive and 
                    focus on positive trends and growth opportunities. Respond with JSON format:
                    {
                        "insights": "string with 2-3 sentences of supportive analysis",
                        "recommendations": ["tip1", "tip2", "tip3"]
                    }
                    """
                },
                {
                    "role": "user", 
                    "content": f"Analyze these mood scores and dates: {json.dumps(entries_data)}"
                }
            ],
            response_format={"type": "json_object"},
        )
        
        return json.loads(response.choices[0].message.content or '{}')
        
    except Exception as e:
        return {
            "insights": "Unable to generate insights at this time.",
            "recommendations": ["Keep journaling regularly", "Practice mindfulness", "Stay connected with loved ones"]
        }
