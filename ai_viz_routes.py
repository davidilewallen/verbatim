from flask import Blueprint, render_template, request, redirect, url_for
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize blueprint
ai_viz = Blueprint("ai_viz", __name__, template_folder="templates")

# Temporary in-memory store for session data
user_inputs = {}

@ai_viz.route("/ai-viz", methods=["GET", "POST"])
def ai_viz_route():
    if request.method == "POST":
        brand = request.form.get("brand")
        competitors = [
            request.form.get("competitor1"),
            request.form.get("competitor2"),
            request.form.get("competitor3"),
        ]
        problem = request.form.get("problem")

        prompt = (
            f"A persona is facing this problem: '{problem}'. "
            f"Create 10 non-branded prompts that a user might input into ChatGPT "
            f"if they were looking for recommendations on companies that have solutions to this problem. These prompts should be general and relevant to this space."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for marketing and brand strategy.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            suggestions = response.choices[0].message.content
            prompts = [q.strip("-• \n") for q in suggestions.split("\n") if q.strip()]

            user_inputs[brand] = {
                "prompts": prompts,
                "competitors": competitors,
                "problem": problem,
            }

            return render_template("ai_viz_prompts.html", brand=brand, prompts=prompts)

        except Exception as e:
            return f"Error generating prompts: {str(e)}"

    return render_template("ai_viz.html")


@ai_viz.route("/run-chat-analysis/<brand>", methods=["GET"])
def run_chat_analysis(brand):
    if brand not in user_inputs:
        return redirect(url_for("ai_viz.ai_viz_route"))

    prompts = user_inputs[brand]["prompts"]
    responses = []

    for query in prompts:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for evaluating brand visibility in natural language platforms.",
                    },
                    {"role": "user", "content": query},
                ],
                temperature=0.5,
                max_tokens=300,
            )

            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error: {str(e)}"

        responses.append({"query": query, "response": answer})
        time.sleep(1.5)  # Prevent hitting rate limits

    return render_template("ai_viz_results.html", brand=brand, results=responses)
