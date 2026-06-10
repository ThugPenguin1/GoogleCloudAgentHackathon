from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from mongodb_tools import (
    log_study_session,
    get_study_recommendations,
    create_desmos_graph,
    check_progress_calibration,
    get_knowledge_tree,
    search_study_materials,
    get_time_schedule,
    get_multimodal_material,
    calibrate_knowledge,
    build_study_dashboard,
    seed_demo_data,
)

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
HOME_PAGE = BASE_DIR / "web" / "index.html"


TOOL_MAP = {
    "log_study_session": log_study_session,
    "get_study_recommendations": get_study_recommendations,
    "create_desmos_graph": create_desmos_graph,
    "check_progress_calibration": check_progress_calibration,
    "get_knowledge_tree": get_knowledge_tree,
    "search_study_materials": search_study_materials,
    "get_time_schedule": get_time_schedule,
    "get_multimodal_material": get_multimodal_material,
    "calibrate_knowledge": calibrate_knowledge,
}


@app.route("/")
def index():
    if HOME_PAGE.exists():
        return Response(HOME_PAGE.read_text(encoding="utf-8"), mimetype="text/html")
    return "Atlas Study Companion MCP Server", 200


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/student/<student_id>/dashboard")
def dashboard(student_id):
    return jsonify(build_study_dashboard(student_id))


@app.route("/admin/seed-demo", methods=["POST"])
def admin_seed_demo():
    return jsonify(seed_demo_data(force=True))


@app.route("/tool/<name>", methods=["POST"])
def call_tool(name):
    func = TOOL_MAP.get(name)
    if not func:
        return jsonify({"status": "error", "message": "tool not found"}), 404

    payload = request.json or {}
    try:
        # Expecting JSON body with appropriate parameters
        res = func(**payload)
        return jsonify(res)
    except TypeError as e:
        return jsonify({"status": "error", "message": f"invalid args: {e}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
