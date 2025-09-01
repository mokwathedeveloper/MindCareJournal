import json
from openai import OpenAI

# Using DeepSeek API with OpenAI-compatible client
DEEPSEEK_API_KEY = "sk-7a45473cf92f47299f8fc23ee5df6667"
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)



def analyze_journal_sentiment(text):
    """
    Analyze the sentiment and emotions in a journal entry using DeepSeek API.
    Returns mood score (1-5), confidence (0-1), and detailed emotions.
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
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
        print(f"DeepSeek API error: {e}")

        # Provide basic sentiment analysis based on keywords as fallback
        text_lower = text.lower()

        # Simple keyword-based mood analysis
        positive_words = ['happy', 'joy', 'great', 'excellent', 'wonderful',
                         'amazing', 'love', 'excited', 'good', 'best',
                         'awesome', 'fantastic']
        negative_words = ['sad', 'depressed', 'angry', 'hate', 'terrible',
                         'awful', 'sick', 'bad', 'worst', 'horrible',
                         'anxious', 'worried']

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Calculate basic mood score
        if positive_count > negative_count:
            if positive_count >= 3:
                mood_score = 5  # Very positive
                emotions = {"happiness": 80, "excitement": 60, "hope": 70,
                          "calm": 40, "sadness": 5, "anxiety": 10,
                          "anger": 5, "fear": 5}
            elif positive_count >= 2:
                mood_score = 4  # Positive
                emotions = {"happiness": 65, "excitement": 40, "hope": 50,
                          "calm": 45, "sadness": 10, "anxiety": 15,
                          "anger": 5, "fear": 10}
            else:
                mood_score = 4  # Slightly positive
                emotions = {"happiness": 50, "excitement": 30, "hope": 40,
                          "calm": 40, "sadness": 15, "anxiety": 20,
                          "anger": 10, "fear": 10}
        elif negative_count > positive_count:
            if negative_count >= 3:
                mood_score = 1  # Very negative
                emotions = {"sadness": 80, "anxiety": 60, "anger": 40,
                          "fear": 30, "happiness": 5, "excitement": 5,
                          "calm": 10, "hope": 10}
            elif negative_count >= 2:
                mood_score = 2  # Negative
                emotions = {"sadness": 60, "anxiety": 45, "anger": 30,
                          "fear": 25, "happiness": 10, "excitement": 10,
                          "calm": 20, "hope": 15}
            else:
                mood_score = 2  # Slightly negative
                emotions = {"sadness": 45, "anxiety": 35, "anger": 20,
                          "fear": 20, "happiness": 15, "excitement": 15,
                          "calm": 25, "hope": 20}
        else:
            mood_score = 3  # Neutral
            emotions = {"happiness": 25, "sadness": 20, "anxiety": 20,
                      "anger": 10, "fear": 15, "excitement": 20,
                      "calm": 40, "hope": 30}

        return {
            "mood_score": mood_score,
            "confidence": 0.6,  # Medium confidence for keyword-based analysis
            "emotions": emotions,
            "analysis_method": "keyword_fallback",
            "api_error": str(e)
        }



def generate_mood_insights(entries_data):
    """
    Generate insights about mood patterns from multiple journal entries using DeepSeek API.
    """
    try:
        if not entries_data:
            return {"insights": "No entries available for analysis."}

        response = client.chat.completions.create(
            model="deepseek-chat",
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
        print(f"DeepSeek API error for insights: {e}")

        # Generate basic insights based on mood data
        if entries_data:
            mood_scores = [entry.get('mood_score', 3) for entry in entries_data]
            avg_mood = sum(mood_scores) / len(mood_scores)

            if avg_mood >= 4:
                insights_text = ("Your recent journal entries show a positive "
                               "emotional pattern. You've been experiencing more "
                               "uplifting moments and maintaining good mental wellness.")
                recommendations = [
                    "Continue the positive practices you've been doing",
                    "Share your success strategies with others",
                    "Maintain your current self-care routine"
                ]
            elif avg_mood >= 3:
                insights_text = ("Your emotional state appears balanced with a "
                               "mix of different feelings. This is normal and "
                               "shows emotional awareness and growth.")
                recommendations = [
                    "Keep journaling to maintain emotional awareness",
                    "Practice mindfulness during challenging moments",
                    "Celebrate small daily victories"
                ]
            else:
                insights_text = ("Your entries suggest you've been going through "
                               "some challenges. Remember that difficult periods "
                               "are temporary and seeking support is a sign of strength.")
                recommendations = [
                    "Consider talking to a trusted friend or counselor",
                    "Practice daily self-care activities",
                    "Focus on small, achievable daily goals"
                ]
        else:
            insights_text = ("Start your wellness journey by writing regular "
                           "journal entries to track your emotional patterns.")
            recommendations = [
                "Write in your journal daily or weekly",
                "Be honest about your feelings",
                "Look for patterns in your emotions"
            ]

        return {
            "insights": insights_text,
            "recommendations": recommendations,
            "analysis_method": "basic_fallback",
            "api_error": str(e)
        }
