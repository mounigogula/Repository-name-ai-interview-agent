import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI(title="AI Interview Agent")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=api_key)


def generate_questions(role, interview_type, difficulty, number_of_questions):

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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html>
<head>
<title>AI Interview Agent</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body {
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg,#667eea,#764ba2);
    margin: 0;
    padding: 30px;
}

.container {
    max-width: 800px;
    margin: auto;
    background: white;
    padding: 35px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

h1 {
    text-align: center;
    color: #333;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}

label {
    display: block;
    font-weight: bold;
    margin-top: 15px;
    margin-bottom: 7px;
}

input, select {
    width: 100%;
    padding: 13px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 16px;
}

button {
    width: 100%;
    margin-top: 25px;
    padding: 15px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #5568d9;
}

.info {
    background: #f2f3ff;
    padding: 15px;
    border-radius: 10px;
    margin-top: 25px;
}

.question {
    background: #f7f7ff;
    border-left: 5px solid #667eea;
    padding: 15px;
    margin-top: 12px;
    border-radius: 8px;
    line-height: 1.6;
}

</style>
</head>

<body>

<div class="container">

<h1>🤖 AI Interview Agent</h1>

<p class="subtitle">
Generate personalized interview questions using AI
</p>

<form method="post" action="/start-interview">

<label>Job Role</label>

<input
    type="text"
    name="role"
    placeholder="Example: Python Developer"
    required
>

<label>Interview Type</label>

<select name="interview_type">

<option value="Technical">Technical</option>
<option value="HR">HR</option>
<option value="Behavioral">Behavioral</option>
<option value="Mixed">Mixed</option>

</select>

<label>Difficulty</label>

<select name="difficulty">

<option value="Easy">Easy</option>
<option value="Medium" selected>Medium</option>
<option value="Hard">Hard</option>

</select>

<label>Number of Questions</label>

<select name="number_of_questions">

<option value="5">5</option>
<option value="10">10</option>
<option value="15">15</option>
<option value="20">20</option>

</select>

<button type="submit">
🚀 Start Interview
</button>

</form>

</div>

</body>
</html>
"""


@app.post("/start-interview", response_class=HTMLResponse)
def start_interview(
    role: str = Form(...),
    interview_type: str = Form(...),
    difficulty: str = Form(...),
    number_of_questions: int = Form(...)
):

    questions = generate_questions(
        role,
        interview_type,
        difficulty,
        number_of_questions
    )

    question_html = ""

    for line in questions.split("\n"):

        line = line.strip()

        if line:
            question_html += f"""
            <div class="question">
                {line}
            </div>
            """

    return f"""
<!DOCTYPE html>

<html>

<head>

<title>AI Interview Questions</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body {{
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg,#667eea,#764ba2);
    margin: 0;
    padding: 30px;
}}

.container {{
    max-width: 800px;
    margin: auto;
    background: white;
    padding: 35px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}}

h1 {{
    text-align: center;
    color: #333;
}}

.info {{
    background: #f2f3ff;
    padding: 15px;
    border-radius: 10px;
    margin: 20px 0;
}}

.question {{
    background: #f7f7ff;
    border-left: 5px solid #667eea;
    padding: 15px;
    margin-top: 12px;
    border-radius: 8px;
    line-height: 1.6;
}}

.back {{
    display: block;
    text-align: center;
    margin-top: 25px;
    padding: 14px;
    background: #667eea;
    color: white;
    text-decoration: none;
    border-radius: 8px;
}}

</style>

</head>

<body>

<div class="container">

<h1>📋 Interview Questions</h1>

<div class="info">

<strong>Role:</strong> {role}<br>
<strong>Interview Type:</strong> {interview_type}<br>
<strong>Difficulty:</strong> {difficulty}<br>
<strong>Questions:</strong> {number_of_questions}

</div>

{question_html}

<a class="back" href="/">
⬅️ Start Another Interview
</a>

</div>

</body>

</html>
"""


@app.get("/docs")
def docs_info():
    return {
        "message": "AI Interview Agent API",
        "endpoint": "/start-interview"
    }
