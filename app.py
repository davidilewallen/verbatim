from flask import Flask, render_template
from ai_viz_routes import ai_viz

app = Flask(__name__)  # ✅ Initialize the app first
app.register_blueprint(ai_viz)  # ✅ Then register the blueprint

@app.route("/")
def home():
    return render_template("index.html")  # Optional landing page

if __name__ == "__main__":
    app.run(debug=True)
