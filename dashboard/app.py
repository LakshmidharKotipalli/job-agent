from flask import Flask, render_template, request, jsonify
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.tracker import Tracker

app = Flask(__name__)
tracker = Tracker()

@app.route("/")
def index():
    sort_by = request.args.get("sort", "score")
    order = request.args.get("order", "desc")
    source = request.args.get("source", "")
    min_score = int(request.args.get("min_score", 0))

    jobs = tracker.get_all_jobs(sort_by=sort_by, order=order,
                                source_filter=source, min_score=min_score)
    stats = tracker.get_stats()
    sources = tracker.get_sources()
    return render_template("index.html", jobs=jobs, stats=stats, sources=sources,
                           current_sort=sort_by, current_order=order,
                           current_source=source, current_min_score=min_score)

@app.route("/job/<int:job_id>")
def job_detail(job_id):
    job = tracker.get_job_by_id(job_id)
    if not job:
        return "Job not found", 404
    cover_letter = tracker.get_cover_letter(job_id)
    return render_template("detail.html", job=job, cover_letter=cover_letter)

@app.route("/api/cover-letter/<int:job_id>")
def api_cover_letter(job_id):
    text = tracker.get_cover_letter(job_id)
    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
