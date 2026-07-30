import os
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from anthropic import Anthropic, APIError

load_dotenv()

app = Flask(__name__, static_folder="public", static_url_path="")

MODEL = "claude-sonnet-5"

TONE_GUIDANCE = {
    "manager": "Direct manager. Practical, clear on status/asks, no fluff, comfortable level of detail.",
    "director_exec": "Director/Exec. High-level, outcome- and risk-focused, minimal jargon, gets to the point fast.",
    "team_qbr": "Team QBR audience. Allowed to be longer and more detailed than other audiences — include context and specifics.",
    "peer": "Peer CSM/colleague. Conversational, collegial, assumes shared context.",
    "cross_functional": "Cross-functional (product, sales, etc.). Assume no CS-specific context; spell out impact in terms relevant to their function.",
}

STYLE_GUIDANCE = {
    "bullet_brief": "Bullet brief: short bulleted list, scannable, no long sentences.",
    "narrative_paragraph": "Narrative paragraph: flowing prose, one or two short paragraphs.",
    "two_sentences": "Two sentences max: extremely concise, at most two sentences total, cut everything non-essential.",
}


def days_until(date_str):
    if not date_str:
        return None
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (target - date.today()).days


def build_prompt(data):
    tone_key = data.get("tone", "manager")
    style_key = data.get("style", "bullet_brief")

    tone_desc = TONE_GUIDANCE.get(tone_key, TONE_GUIDANCE["manager"])
    style_desc = STYLE_GUIDANCE.get(style_key, STYLE_GUIDANCE["bullet_brief"])

    account_name = data.get("accountName", "").strip()
    recent_activity = data.get("recentActivity", "").strip()
    follow_up = data.get("followUp", "").strip()
    risk_status = data.get("riskStatus", "").strip()
    risk_notes = data.get("riskNotes", "").strip()
    renewal_date = data.get("renewalDate", "").strip()

    remaining = days_until(renewal_date)
    flag_renewal = remaining is not None and 0 <= remaining <= 120
    renewal_line = "(none provided)"
    if renewal_date:
        renewal_line = renewal_date
        if flag_renewal:
            renewal_line += f" — {remaining} days out. This falls within the 90-120 day window: surface it prominently in the update."
        else:
            renewal_line += " — outside the 90-120 day window, mention only briefly or omit."

    lines = [
        "You are helping a Customer Success Manager write an account update for internal sharing.",
        f"Audience: {tone_desc}",
        f"Output format: {style_desc}",
        "",
        f"Account: {account_name or '(not provided)'}",
        f"Recent activity: {recent_activity or '(not provided)'}",
        f"Follow-up from last update: {follow_up or '(none)'}",
        f"Risk / health status: {risk_status or '(not provided)'}",
        f"Risk / health notes: {risk_notes or '(none)'}",
        f"Renewal date: {renewal_line}",
        "",
        "Write the update now. Follow the output format strictly. "
        "Do not include a subject line, greeting, or sign-off — just the update body. "
        "Do not invent facts not given above.",
    ]
    return "\n".join(lines)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True, silent=True) or {}

    if not data.get("accountName", "").strip():
        return jsonify({"error": "Account name is required."}), 400
    if not data.get("recentActivity", "").strip():
        return jsonify({"error": "Recent activity is required."}), 400

    api_key = data.get("apiKey", "").strip() or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "Add your Anthropic API key above, then try again."}), 400

    prompt = build_prompt(data)

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
    except APIError as e:
        return jsonify({"error": f"Claude API error: {e}"}), 502

    return jsonify({"update": text.strip()})


if __name__ == "__main__":
    app.run(port=5050, debug=True)
