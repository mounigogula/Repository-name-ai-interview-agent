
import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI(title="AI Interview Agent")

# Gemini setup
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=api_key)

chat = client.chats.create(
    model="gemini-3.6-flash"
)


class InterviewRequest(BaseModel):
    role: str
    interview_type: str
    difficulty: str
    number_of_questions: int


def generate_questions(
    role,
    interview_type,
    difficulty,
    number_of_questions
):
    prompt = f"""
You are an AI interviewer.

Generate {number_of_questions} interview questions.

Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}

Rules:
- Number the questions from 1 to {number_of_questions}.
- Keep the questions appropriate for the role.
- For technical interviews, focus on relevant technical concepts.
- Return only the questions.
"""

    response = chat.send_message(prompt)

    return response.text


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Interview Agent API is running"
    }


@app.post("/generate-interview")
def generate_interview(request: InterviewRequest):

    questions = generate_questions(
        role=request.role,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        number_of_questions=request.number_of_questions
    )

    return {
        "role": request.role,
        "interview_type": request.interview_type,
        "difficulty": request.difficulty,
        "number_of_questions": request.number_of_questions,
        "questions": questions
    }
