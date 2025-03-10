import streamlit as st

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class AthleteSwot(BaseModel):
    biodata: str = Field(..., description='Summary of the athlete biodata. This explains who the athlete is, their age, their current status, and their overall swimming career.')
    strengths: str = Field(..., description='Athlete strength points. What are they good at?')
    weaknesses: str = Field(..., description='Athlete weakness points. What are they bad at?')
    opportunities: str = Field(..., description='Athlete opportunities. What can they improve on?')
    threats: str = Field(..., description='Athlete threats. What can hinder their performance?')
    best_stroke: str = Field(..., description='Athlete best stroke based on the available data. Should be 1 of the following: freestyle, backstroke, breaststroke, butterfly. Explain shortly why.')
    best_distance: str = Field(..., description='Athlete best distance based on the available data. What is their best distance?. The distance should be 1 of the following: sprint, middle distance, long distance. Explain shortly why.')
    weakest_stroke: str = Field(..., description='Athlete weakest stroke based on the available data. Should be 1 of the following: freestyle, backstroke, breaststroke, butterfly. Must be different from the best stroke. Explain shortly why.')
    weakest_distance: str = Field(..., description='Athlete weakest distance based on the available data. Should be 1 of the following: sprint, middle distance, long distance. Must be different from the best distance. Explain shortly why.')
    medley: str = Field(..., description='Based on the available data, should the athlete focus on medley events? Yes, No, or Maybe. Explain why.')
    specialization: str = Field(..., description='Athlete specialization. Considering their age, potential growth, and current performance, should they start specializing in a specific stroke or distance? Yes, No, or Maybe. Prioritize Yes or No, only use Maybe if you are unsure. For younger athletes, it is recommended to focus on all strokes and distances. For older athletes, it is recommended to start specializing. Explain why.')
    development_plan: str = Field(..., description='Athlete development plan. What kind of swimmer should they aim to be? Is it a sprinter, distance swimmer, all-rounder, or anything else?')
    short_term_goals: str = Field(..., description='Athlete short term goals. What should they aim to achieve in the next 6 months or in the minor competitions? Should be specific, measurable, achievable, relevant, and time-bound.')
    long_term_goals: str = Field(..., description='Athlete long term goals. What should they aim to achieve in the next 1 year or in the major competitions? Should be specific, measurable, achievable, relevant, and time-bound.')

@st.cache_resource(ttl='1d')
def analyze_athlete_stats(bio: str, stats: dict):
    prompt = f"""
    {st.secrets.gemini_llm.persona}

    Here is the athlete's bio that you will analyze:
    {bio}
    Note: INACTIVE means the athlete is not currently competing or already retired and never come to training anymore. SEMI-ACTIVE means the athlete is competing but not as often as before, maybe around 1-2 times a year because of other commitments like school or work and only come to training when near competition. ACTIVE means the athlete is competing regularly and come to training consistently.

    Here is the athelete's statistics that you will analyze:
    {stats}
    """

    client = genai.Client(api_key=st.secrets.gemini_llm.api_key)

    response = client.models.generate_content(
        model=st.secrets.gemini_llm.model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=AthleteSwot,
            temperature=0.2,
            top_p=0.8,
            top_k=40,
        )
    )

    return response
