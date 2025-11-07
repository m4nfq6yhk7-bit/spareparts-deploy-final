from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
from datetime import datetime
import os

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

# -----------------------------
# Initialize Firebase Admin
# -----------------------------
cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = admin_firestore.client()

# -----------------------------
# Helper Functions
# -----------------------------
def get_all_parts():
    """ดึงข้อมูลอะไหล่ทั้งหมด"""
    parts_ref = db.collection('parts')
    docs = parts_ref.stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]

def get_part_by_id(part_id):
    """ดึงอะไหล่ตาม ID"""
    doc = db.collection('parts').document(part_id).get()
    if doc.exists:
        return {**doc.to_dict(), "id": doc.id}
    return None

def add_transaction(part_id, change_qty, user):
    """บันทึกการเปลี่ยนแปลงสต็อก"""
    txn_ref = db.collection('transactions')
    txn_ref.add({
        "part_id": part_id,
        "change_qty": change_qty,
        "user": user,
        "timestamp": datetime.utcnow()
    })

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    parts = get_all_parts()
    return render_template("dashboard.html", parts=parts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        # ตัวอย่าง login แบบง่าย, สามารถปรับใช้ Firebase Auth ได้
        if email == "admin@kinpo.com" and password == "123456":
            session["user"] = email
            return redirect(url_for("home"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/update_stock", methods=["POST"])
def update_stock():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    part_id = request.form["part_id"]
    new_qty = int(request.form["new_qty"])
    part = get_part_by_id(part_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    db.collection("parts").document(part_id).update({"stockQty": new_qty})
    add_transaction(part_id, new_qty - part["stockQty"], session["user"])
    return jsonify({"success": True, "new_qty": new_qty})

@app.route("/backup")
def backup_firestore():
    """Backup Firestore collection 'parts' to GCS bucket"""
    import json
    from google.cloud import storage

    bucket_name = os.environ.get("FIREBASE_BUCKET")
    if not bucket_name:
        return "FIREBASE_BUCKET not set", 500

    parts = get_all_parts()
    backup_filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(backup_filename)
    blob.upload_from_string(json.dumps(parts, indent=2), content_type="application/json")
    return f"Backup saved to {backup_filename}"

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
