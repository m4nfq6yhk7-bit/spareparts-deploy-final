# SpareParts Inventory Deploy Pack

## ขั้นตอน deploy

1. วางไฟล์ `serviceAccountKey.json` จริงในโฟลเดอร์นี้ (ไม่ commit ขึ้น GitHub)
2. เปลี่ยนชื่อไฟล์ `.env.example` เป็น `.env` และใส่ค่า environment variables ให้ตรงกับ project ของคุณ
3. Push ขึ้น GitHub
4. กด Deploy บน Render
5. ระบบจะรัน `backup_firestore.py` เพื่อ backup Firestore ไปยัง Google Cloud Storage

**หมายเหตุ**:  
- อย่าลืมเพิ่ม `serviceAccountKey.json` ลงใน Render Secret
