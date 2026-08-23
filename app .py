import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>AI Interview Agent</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            min-height: 100vh;
            padding: 30px 15px;
        }

        .container {
            max-width: 850px;
            margin: auto;
            background: white;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 36px;
        }

        .header p {
            color: #666;
            font-size: 17px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }

        input,
        select {
            width: 100%;
            padding: 14px;
            border: 1px solid #ccc;
            border-radius: 10px;
            font-size: 16px;
        }

        input:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            width: 100%;
            padding: 15px;
            margin-top: 5px;
            border: none;
            border-radius: 10px;
            background: #667eea;
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #5568d9;
        }

        button:disabled {
            background: #999;
            cursor: not-allowed;
        }

        #loading {
            display: none;
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            font-weight: bold;
        }

        #error {
            display: none;
            margin-top: 20px;
            padding: 15px;
            background: #ffe5e5;
            color: #c62828;
            border-radius: 10px;
        }

        #result {
            display: none;
            margin-top: 30px;
        }

        #result h2 {
            color: #333;
        }

        .info {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }

        .badge {
            background: #eef0ff;
            color: #4c5bd4;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }

        .question-box {
            background: #f7f8ff;
            border-left: 5px solid #667eea;
            padding: 18px;
            border-radius: 10px;
            margin-bottom: 15px;
            line-height: 1.6;
            color: #333;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            color: #777;
            font-size: 14px;
        }

        @media (max-width: 600px) {
            .container {
                padding: 25px 20px;
            }

            .header h1 {
                font-size: 28px;
            }
        }
    </style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>🤖 AI Interview Agent</h1>
        <p>Generate personalized interview questions using AI</p>
    </div>

    <div class="form-group">
        <label>Job Role</label>

        <input
            type="text"
            id="role"
            placeholder="Example: Python Developer"
        >
    </div>

    <div class="form-group">
        <label>Interview Type</label>

        <select id="interview_type">
            <option value="Technical">Technical</option>
            <option value="HR">HR</option>
            <option value="Behavioral">Behavioral</option>
            <option value="Mixed">Mixed</option>
        </select>
    </div>

    <div class="form-group">
        <label>Difficulty</label>

        <select id="difficulty">
            <option value="Easy">Easy</option>
            <option value="Medium" selected>Medium</option>
            <option value="Hard">Hard</option>
        </select>
    </div>

    <div class="form-group">
        <label>Number of Questions</label>

        <select id="number_of_questions">
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="15">15</option>
            <option value="20">20</option>
        </select>
    </div>

    <button id="generateButton" onclick="generateInterview()">
        🚀 Start Interview
    </button>

    <div id="loading">
        ⏳ AI is generating your interview questions...
    </div>

    <div id="error"></div>

    <div id="result">

        <h2>📋 Interview Questions</h2>

        <div class="info">
            <div class="badge" id="roleBadge"></div>
            <div class="badge" id="typeBadge"></div>
            <div class="badge" id="difficultyBadge"></div>
            <div class="badge" id="countBadge"></div>
        </div>

        <div id="questions"></div>

    </div>

    <div class="footer">
        Powered by AI Interview Agent
    </div>

</div>


<script>

async function generateInterview() {

    const roleInput = document.getElementById("role");

    const role = roleInput.value.trim();

    const interviewType =
        document.getElementById("interview_type").value;

    const difficulty =
        document.getElementById("difficulty").value;

    const numberOfQuestions =
        parseInt(
            document.getElementById("number_of_questions").value
        );

    const button =
        document.getElementById("generateButton");

    const loading =
        document.getElementById("loading");

    const result =
        document.getElementById("result");

    const error =
        document.getElementById("error");

    const questionsDiv =
        document.getElementById("questions");


    if (role === "") {

        alert("Please enter a job role.");

        roleInput.focus();

        return;
    }


    button.disabled = true;

    button.innerHTML =
        "⏳ Generating Questions...";

    loading.style.display = "block";

    result.style.display = "none";

    error.style.display = "none";


    try {

        const response = await fetch(
            window.location.origin + "/generate-interview",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify({
                    role: role,
                    interview_type: interviewType,
                    difficulty: difficulty,
                    number_of_questions: numberOfQuestions
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Failed to generate questions."
            );

        }


        if (!data.questions) {

            throw new Error(
                "The AI did not return any questions."
            );

        }


        document.getElementById("roleBadge").textContent =
            "Role: " + data.role;

        document.getElementById("typeBadge").textContent =
            "Type: " + data.interview_type;

        document.getElementById("difficultyBadge").textContent =
            "Difficulty: " + data.difficulty;

        document.getElementById("countBadge").textContent =
            "Questions: " + data.number_of_questions;


        questionsDiv.innerHTML = "";


        const questionLines =
            data.questions.split("\n");


        questionLines.forEach(function(line) {

            const text = line.trim();

            if (text !== "") {

                const questionBox =
                    document.createElement("div");

                questionBox.className =
                    "question-box";

                questionBox.textContent = text;

                questionsDiv.appendChild(
                    questionBox
                );

            }

        });


        result.style.display = "block";


        result.scrollIntoView({
            behavior: "smooth"
        });


    } catch (errorObject) {

        error.textContent =
            "❌ " + errorObject.message;

        error.style.display = "block";


    } finally {

        loading.style.display = "none";

        button.disabled = false;

        button.innerHTML =
            "🚀 Start Interview";

    }

}

</script>

</body>
</html>
"""


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
