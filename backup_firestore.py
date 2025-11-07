import os
from google.cloud import firestore
from google.cloud import storage
from datetime import datetime

PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
BUCKET_NAME = os.getenv("FIREBASE_BUCKET")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "serviceAccountKey.json"
db = firestore.Client(project=PROJECT_ID)

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

def backup_firestore():
    collections = db.collections()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"firestore_backup_{timestamp}.json"
    
    data = {}
    for col in collections:
        docs = col.stream()
        data[col.id] = {doc.id: doc.to_dict() for doc in docs}

    with open(backup_file, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)

    blob = bucket.blob(backup_file)
    blob.upload_from_filename(backup_file)
    print(f"Backup uploaded to {BUCKET_NAME}/{backup_file}")

if __name__ == "__main__":
    backup_firestore()
