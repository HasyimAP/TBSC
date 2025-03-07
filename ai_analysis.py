import streamlit as st

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class AthleteSwot(BaseModel):
    biodata: str = Field(..., description='Summary of the athlete biodata.')
    strengths: str = Field(..., description='Athlete strength points. What are they good at?')
    weaknesses: str = Field(..., description='Athlete weakness points. What are they bad at?')
    opportunities: str = Field(..., description='Athlete opportunities. What can they improve on?')
    threats: str = Field(..., description='Athlete threats. What can hinder their performance?')
    best_stroke: str = Field(..., description='Athlete best stroke based on the available data. Should be 1 of the following: freestyle, backstroke, breaststroke, butterfly.')
    best_distance: str = Field(..., description='Athlete best distance based on the available data. What is their best distance?. The distance should be 1 of the following: sprint, middle distance, long distance.')
    weakest_stroke: str = Field(..., description='Athlete weakest stroke based on the available data. Should be 1 of the following: freestyle, backstroke, breaststroke, butterfly.')
    weakest_distance: str = Field(..., description='Athlete weakest distance based on the available data. Should be 1 of the following: sprint, middle distance, long distance.')
    medley: str = Field(..., description='Based on the available data, should the athlete focus on medley events? Yes or No. Explain why.')
    development_plan: str = Field(..., description='Athlete development plan. What kind of swimmer should they aim to be? Is it a sprinter, distance swimmer, all-rounder, or anything else?')
    short_term_goals: str = Field(..., description='Athlete short term goals. What should they aim to achieve in the next 6 months? Should be specific, measurable, achievable, relevant, and time-bound.')
    long_term_goals: str = Field(..., description='Athlete long term goals. What should they aim to achieve in the next 1 year? Should be specific, measurable, achievable, relevant, and time-bound.')

@st.cache_resource(ttl='1d')
def analyze_athlete_stats(bio: str, stats: dict):
    prompt = f"""
    {st.secrets.gemini_llm.persona}

    Here is the athlete's bio that you will analyze:
    {bio}
    Note: INACTIVE means the athlete is not currently competing or already retired. SEMI-ACTIVE means the athlete is competing but not as often as before, maybe around 1-2 times a year because of other commitments.

    Here is the athelete's statistics that you will analyze:
    {stats}

    The output should be modeled after this Pydanctic data model schema in JSON format:
    {AthleteSwot.model_json_schema()}
    """

    client = genai.Client(api_key=st.secrets.gemini_llm.api_key)

    response = client.models.generate_content(
        model=st.secrets.gemini_llm.model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=AthleteSwot,
            temperature=0.5,
        )
    )

    return response

# st.write('AI persona:', st.secrets.gemini_llm.persona)