import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote_plus
from pymongo import MongoClient

_client = None
_db = None
_seeded = False

DEMO_STUDENT_ID = "21200184"
DEMO_SAMPLE_FILE = Path(__file__).resolve().parent / "sample_data.json"


def get_db():
    global _client, _db
    if _db is not None:
        return _db

    mongo_uri = os.environ.get("MONGODB_URI") or os.environ.get("MONGO_URI")
    if not mongo_uri:
        raise EnvironmentError("Set MONGODB_URI in the environment")

    _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)
    _db = _client.get_default_database()
    return _db


def _normalize_seed_doc(collection_name, doc):
    doc = dict(doc)
    if collection_name == "study_sessions" and isinstance(doc.get("timestamp"), str):
        try:
            doc["timestamp"] = datetime.fromisoformat(doc["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pass
    return doc


def seed_demo_data(force=False):
    global _seeded
    db = get_db()
    if _seeded and not force:
        return {"status": "ok", "message": "demo data already seeded"}

    if not DEMO_SAMPLE_FILE.exists():
        return {"status": "error", "message": "sample_data.json not found"}

    with DEMO_SAMPLE_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    inserted = {}
    for collection_name, docs in data.items():
        if not isinstance(docs, list) or not docs:
            continue

        collection = db[collection_name]
        existing_ids = set()
        if collection_name == "students":
            existing_ids = {str(item.get("_id")) for item in collection.find({}, {"_id": 1})}
        elif collection_name in {"study_sessions", "materials", "knowledge_trees", "student_notes"}:
            existing_ids = set()

        normalized_docs = []
        for doc in docs:
            normalized_doc = _normalize_seed_doc(collection_name, doc)
            if collection_name == "students":
                if str(normalized_doc.get("_id")) in existing_ids:
                    continue
            elif collection_name in {"study_sessions", "materials", "knowledge_trees", "student_notes"}:
                if str(normalized_doc.get("student_id")) != DEMO_STUDENT_ID:
                    continue
            normalized_docs.append(normalized_doc)

        if normalized_docs:
            collection.insert_many(normalized_docs)
            inserted[collection_name] = len(normalized_docs)

    _seeded = True
    return {"status": "ok", "inserted": inserted}


def _parse_timestamp(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _student_sessions(db, student_id):
    sessions = []
    for doc in db.study_sessions.find({"student_id": str(student_id)}):
        parsed = _parse_timestamp(doc.get("timestamp"))
        doc["_parsed_timestamp"] = parsed
        sessions.append(doc)

    sessions.sort(
        key=lambda item: item.get("_parsed_timestamp") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return sessions


def _student_goal_subjects(student):
    goals = student.get("semester_goals", {}) or {}
    return list(goals.keys())


def _subject_progress(student, sessions):
    goals = student.get("semester_goals", {}) or {}
    progress = []
    sessions_by_subject = {}

    for session in sessions:
        subject = session.get("subject")
        if not subject:
            continue
        sessions_by_subject.setdefault(subject, []).append(session)

    for subject, goal_topics in goals.items():
        goal_topics = list(goal_topics or [])
        subject_sessions = sessions_by_subject.get(subject, [])
        covered_topics = {item.get("topic") for item in subject_sessions if item.get("topic")}
        recent_minutes = sum(int(item.get("duration_minutes", 0)) for item in subject_sessions if item.get("_parsed_timestamp"))
        percent_complete = int((len(covered_topics) / max(1, len(goal_topics))) * 100)
        remaining_topics = [topic for topic in goal_topics if topic not in covered_topics]
        next_topic = remaining_topics[0] if remaining_topics else (goal_topics[0] if goal_topics else subject)
        last_studied = subject_sessions[0].get("_parsed_timestamp") if subject_sessions else None

        progress.append(
            {
                "subject": subject,
                "goal_topics": goal_topics,
                "recent_minutes": recent_minutes,
                "covered_topics": sorted(covered_topics),
                "remaining_topics": remaining_topics,
                "next_topic": next_topic,
                "percent_complete": percent_complete,
                "last_studied": last_studied.isoformat() if last_studied else None,
            }
        )

    progress.sort(key=lambda item: (item["percent_complete"], item["recent_minutes"]))
    return progress


def log_study_session(student_id, subject, topic, duration_minutes):
    db = get_db()
    doc = {
        "student_id": str(student_id),
        "subject": subject,
        "topic": topic,
        "duration_minutes": int(duration_minutes),
        "timestamp": datetime.now(timezone.utc),
    }
    res = db.study_sessions.insert_one(doc)
    return {"status": "ok", "inserted_id": str(res.inserted_id)}


def get_study_recommendations(student_id):
    db = get_db()
    student = db.students.find_one({"_id": str(student_id)})
    if not student:
        return {"status": "error", "message": "student not found"}

    cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    sessions = _student_sessions(db, student_id)
    recent_sessions = [session for session in sessions if session.get("_parsed_timestamp") and session["_parsed_timestamp"] >= cutoff]
    studied_by_subject = {}
    for session in recent_sessions:
        subject = session.get("subject")
        studied_by_subject.setdefault(subject, 0)
        studied_by_subject[subject] += int(session.get("duration_minutes", 0))

    subject_progress = _subject_progress(student, sessions)
    target = max(1, student.get("weekly_target_minutes", 600))
    recommendations = []

    for item in subject_progress:
        recent_minutes = studied_by_subject.get(item["subject"], 0)
        focus_reason = "Low recent study time" if recent_minutes < target / max(1, len(subject_progress)) else "Good momentum, keep it warm"
        if item["remaining_topics"]:
            focus_reason = f"Next gap: {item['remaining_topics'][0]}"

        recommendations.append(
            {
                "subject": item["subject"],
                "recent_minutes": recent_minutes,
                "percent_complete": item["percent_complete"],
                "next_topic": item["next_topic"],
                "reason": focus_reason,
            }
        )

    recommendations.sort(key=lambda item: (item["percent_complete"], item["recent_minutes"]))
    return {
        "status": "ok",
        "student_id": str(student_id),
        "recommendations": recommendations,
    }


def create_desmos_graph(equation):
    # Minimal URL encoding for a single expression
    expr = quote_plus(equation)
    url = f"https://www.desmos.com/calculator?expressions[0]={expr}"
    return {"status": "ok", "desmos_url": url}


def check_progress_calibration(student_id, subject):
    db = get_db()
    student = db.students.find_one({"_id": str(student_id)})
    if not student:
        return {"status": "error", "message": "student not found"}

    goal_topics = student.get("semester_goals", {}).get(subject, [])
    if not goal_topics:
        return {"status": "error", "message": "no goals for subject"}

    sessions = _student_sessions(db, student_id)
    subject_sessions = [item for item in sessions if item.get("subject") == subject]
    covered = set(item.get("topic") for item in subject_sessions if item.get("topic"))
    percent = int((len(covered) / max(1, len(goal_topics))) * 100)
    remaining_topics = [topic for topic in goal_topics if topic not in covered]
    recent_minutes = sum(int(item.get("duration_minutes", 0)) for item in subject_sessions)

    if percent >= 85:
        recommendation = "You are ahead of the semester plan. Focus on review and mixed practice."
    elif percent >= 60:
        recommendation = f"You are on track. Close your remaining gaps: {', '.join(remaining_topics[:2]) or 'keep reviewing'}"
    else:
        recommendation = f"Increase focus on: {', '.join(remaining_topics[:3]) or subject}"

    return {
        "status": "ok",
        "subject": subject,
        "percent_complete": percent,
        "recent_minutes": recent_minutes,
        "mastered_topics": sorted(covered),
        "remaining_topics": remaining_topics,
        "recommendation": recommendation,
    }


def get_knowledge_tree(student_id, subject):
    db = get_db()
    doc = db.knowledge_trees.find_one({"student_id": str(student_id), "subject": subject})
    if not doc:
        return {"status": "error", "message": "knowledge tree not found"}
    return {"status": "ok", "tree": doc.get("tree", {})}


def search_study_materials(student_id, search_term):
    db = get_db()
    # Basic text search using $text if available, otherwise regex fallback
    try:
        results = list(db.materials.find({"$text": {"$search": search_term}, "student_id": str(student_id)}).limit(20))
    except Exception:
        import re
        regex = re.compile(search_term, re.IGNORECASE)
        results = list(db.materials.find({"student_id": str(student_id), "$or": [{"title": regex}, {"content": regex}]}).limit(20))

    clean = []
    for r in results:
        r["_id"] = str(r.get("_id"))
        clean.append({k: v for k, v in r.items() if k in ("_id", "title", "subject", "type")})

    return {"status": "ok", "matches": clean}


def get_time_schedule(student_id):
    """Time scheduler so that it tells you in which week to study what based on semester goals."""
    db = get_db()
    student = db.students.find_one({"_id": str(student_id)})
    if not student:
        return {"status": "error", "message": "student not found"}

    sessions = _student_sessions(db, student_id)
    subject_progress = _subject_progress(student, sessions)
    if not subject_progress:
        return {"status": "error", "message": "no semester goals found"}

    weeks = [f"Week {index}" for index in range(1, 9)]
    schedule = []
    week_index = 0

    for subject_item in subject_progress:
        topic_pool = subject_item["remaining_topics"] or subject_item["goal_topics"]
        if not topic_pool:
            continue
        for topic in topic_pool:
            schedule.append(
                {
                    "week": weeks[week_index % len(weeks)],
                    "subject": subject_item["subject"],
                    "topic": topic,
                    "priority": "high" if subject_item["percent_complete"] < 60 else "medium",
                }
            )
            week_index += 1

    return {
        "status": "ok",
        "student_id": str(student_id),
        "schedule": schedule,
    }


def get_multimodal_material(topic):
    """Learning assistant that provides 3 things: text, image, and audio resources."""
    import urllib.parse
    encoded = urllib.parse.quote(topic)
    return {
        "status": "ok",
        "topic": topic,
        "title": f"Learning pack: {topic}",
        "text_summary": f"{topic} summary: start with the definition, then work through the mechanism, one worked example, and a quick self-check question.",
        "image_url": f"https://image.dummy/search?q={encoded}",
        "audio_url": f"https://audio.dummy/explain?q={encoded}",
        "practice_prompt": f"Explain {topic} in your own words, then solve one short problem without notes.",
    }


def calibrate_knowledge(student_id, subject, known_topics):
    """Calibrator to learn about what the user already knows and update their profile."""
    db = get_db()
    if isinstance(known_topics, str):
        known_topics = [known_topics]

    unique_topics = [topic for topic in dict.fromkeys(topic.strip() for topic in known_topics if topic and topic.strip())]
    db.students.update_one(
        {"_id": str(student_id)},
        {
            "$addToSet": {f"known_topics.{subject}": {"$each": unique_topics}},
            "$set": {"last_calibrated_at": datetime.now(timezone.utc)},
        },
        upsert=True,
    )
    updated_student = db.students.find_one({"_id": str(student_id)}) or {}
    known = updated_student.get("known_topics", {}).get(subject, []) if isinstance(updated_student.get("known_topics"), dict) else []
    return {
        "status": "ok",
        "subject": subject,
        "known_topics": known,
        "message": f"Successfully updated your knowledge profile for {subject}.",
    }


def build_study_dashboard(student_id):
    db = get_db()
    student = db.students.find_one({"_id": str(student_id)})
    if not student:
        if str(student_id) == DEMO_STUDENT_ID:
            seed_result = seed_demo_data(force=True)
            if seed_result.get("status") == "ok":
                student = db.students.find_one({"_id": str(student_id)})
        if not student:
            return {"status": "error", "message": "student not found"}

    sessions = _student_sessions(db, student_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    recent_sessions = [item for item in sessions if item.get("_parsed_timestamp") and item["_parsed_timestamp"] >= cutoff]
    subject_progress = _subject_progress(student, sessions)

    minutes_14d = sum(int(item.get("duration_minutes", 0)) for item in recent_sessions)
    sessions_14d = len(recent_sessions)
    average_progress = int(
        sum(item["percent_complete"] for item in subject_progress) / max(1, len(subject_progress))
    )
    most_recent_focus = subject_progress[0]["subject"] if subject_progress else None
    neglected_subjects = [item["subject"] for item in sorted(subject_progress, key=lambda item: (item["recent_minutes"], item["percent_complete"]))]

    materials = list(
        db.materials.find({"student_id": str(student_id)}, {"title": 1, "subject": 1, "type": 1, "tags": 1}).limit(20)
    )
    knowledge_trees = list(db.knowledge_trees.find({"student_id": str(student_id)}))
    tree_map = {item.get("subject"): item.get("tree", {}) for item in knowledge_trees}

    return {
        "status": "ok",
        "student": {
            "id": str(student_id),
            "name": student.get("name", "Student"),
            "weekly_target_minutes": student.get("weekly_target_minutes", 600),
        },
        "overview": {
            "minutes_14d": minutes_14d,
            "sessions_14d": sessions_14d,
            "subjects_tracked": len(subject_progress),
            "average_progress": average_progress,
            "focus_subject": most_recent_focus,
            "neglected_subjects": neglected_subjects,
        },
        "subjects": subject_progress,
        "schedule": get_time_schedule(student_id).get("schedule", []),
        "recommendations": get_study_recommendations(student_id).get("recommendations", []),
        "recent_sessions": [
            {
                "subject": item.get("subject"),
                "topic": item.get("topic"),
                "duration_minutes": item.get("duration_minutes"),
                "timestamp": item.get("_parsed_timestamp").isoformat() if item.get("_parsed_timestamp") else None,
            }
            for item in recent_sessions[:10]
        ],
        "materials": [
            {
                "title": item.get("title"),
                "subject": item.get("subject"),
                "type": item.get("type"),
                "tags": item.get("tags", []),
            }
            for item in materials
        ],
        "knowledge_trees": tree_map,
    }
