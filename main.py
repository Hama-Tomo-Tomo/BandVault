from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS bands (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, band_id INTEGER, date TEXT, location TEXT, FOREIGN KEY (band_id) REFERENCES bands(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS setlists (id INTEGER PRIMARY KEY AUTOINCREMENT, band_id INTEGER, title TEXT, FOREIGN KEY (band_id) REFERENCES bands(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS setlist_songs (id INTEGER PRIMARY KEY AUTOINCREMENT, setlist_id INTEGER, play_order INTEGER, song_name TEXT, gear_note TEXT, FOREIGN KEY (setlist_id) REFERENCES setlists(id))")
    
    test_bands = ["ずっと珠でいいのに。", "ヨシムラ", "メスの極み綾部。"]
    for band in test_bands:
        try: cursor.execute("INSERT INTO bands (name) VALUES (?)", (band,))
        except sqlite3.IntegrityError: pass
            
    cursor.execute("SELECT count(*) FROM events")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id FROM bands WHERE name = 'ずっと珠でいいのに。'")
        band_row = cursor.fetchone()
        if band_row:
            band_id = band_row[0]
            events_data = [(band_id, "2024-05-01", "ホンダ楽器"), (band_id, "2024-06-10", "RSEスタジオ")]
            cursor.executemany("INSERT INTO events (band_id, date, location) VALUES (?, ?, ?)", events_data)
            cursor.execute("INSERT INTO setlists (band_id, title) VALUES (?, ?)", (band_id, "基本セットリスト"))
            setlist_id = cursor.lastrowid
            songs_data = [
                (setlist_id, 1, "秒針を噛む", ""),
                (setlist_id, 2, "低血ボルト", ""),
                (setlist_id, 3, "ハゼ馳せる果てるまで", ""),
                (setlist_id, 4, "勘冴えて悔しいわ", "イントロでオーバードライブを踏む")
            ]
            cursor.executemany("INSERT INTO setlist_songs (setlist_id, play_order, song_name, gear_note) VALUES (?, ?, ?, ?)", songs_data)
    conn.commit()
    conn.close()

init_db()

# --- APIエンドポイント（読み取り） ---
@app.get("/")
def read_root(): return {"message": "BandVault API"}

@app.get("/api/bands")
def get_bands():
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM bands")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in rows]

@app.get("/api/bands/{band_id}")
def get_band(band_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM bands WHERE id = ?", (band_id,))
    row = cursor.fetchone()
    conn.close()
    return {"id": row[0], "name": row[1]} if row else {"error": "Band not found"}

@app.get("/api/bands/{band_id}/events")
def get_events(band_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, location FROM events WHERE band_id = ? ORDER BY date DESC", (band_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "date": row[1], "location": row[2]} for row in rows]

@app.get("/api/bands/{band_id}/setlists")
def get_setlists(band_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM setlists WHERE band_id = ?", (band_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "title": row[1]} for row in rows]

@app.get("/api/setlists/{setlist_id}/songs")
def get_setlist_songs(setlist_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, play_order, song_name, gear_note FROM setlist_songs WHERE setlist_id = ? ORDER BY play_order ASC", (setlist_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "play_order": row[1], "song_name": row[2], "gear_note": row[3]} for row in rows]

# --- APIエンドポイント（書き込み：POST） ---
class BandCreate(BaseModel): name: str
class EventCreate(BaseModel): date: str; location: str
class SetlistCreate(BaseModel): title: str
class SongCreate(BaseModel): song_name: str; gear_note: str

@app.post("/api/bands")
def create_band(band: BandCreate):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bands (name) VALUES (?)", (band.name,))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {"id": new_id, "name": band.name}
    except sqlite3.IntegrityError:
        conn.close()
        return {"error": "already exists"}

@app.post("/api/bands/{band_id}/events")
def create_event(band_id: int, event: EventCreate):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (band_id, date, location) VALUES (?, ?, ?)", (band_id, event.date, event.location))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "date": event.date, "location": event.location}

@app.post("/api/bands/{band_id}/setlists")
def create_setlist(band_id: int, setlist: SetlistCreate):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO setlists (band_id, title) VALUES (?, ?)", (band_id, setlist.title))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": setlist.title}

@app.post("/api/setlists/{setlist_id}/songs")
def create_song(setlist_id: int, song: SongCreate):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM setlist_songs WHERE setlist_id = ?", (setlist_id,))
    next_order = cursor.fetchone()[0] + 1
    cursor.execute("INSERT INTO setlist_songs (setlist_id, play_order, song_name, gear_note) VALUES (?, ?, ?, ?)", (setlist_id, next_order, song.song_name, song.gear_note))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "play_order": next_order, "song_name": song.song_name, "gear_note": song.gear_note}

# --- データの削除（DELETE）処理 ---
@app.delete("/api/bands/{band_id}")
def delete_band(band_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bands WHERE id = ?", (band_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

@app.delete("/api/setlists/{setlist_id}")
def delete_setlist(setlist_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM setlists WHERE id = ?", (setlist_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

# 新規追加：セットリスト内の曲を削除
@app.delete("/api/songs/{song_id}")
def delete_song(song_id: int):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM setlist_songs WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

# 新規追加：曲順を再保存する処理のデータ定義と窓口（PUT）
class ReorderData(BaseModel):
    song_ids: list[int]

@app.put("/api/setlists/{setlist_id}/reorder")
def reorder_songs(setlist_id: int, data: ReorderData):
    conn = sqlite3.connect("bandvault.db")
    cursor = conn.cursor()
    # 送られてきた順番通りに、play_order（1番目、2番目...）を上書き更新する
    for index, song_id in enumerate(data.song_ids):
        cursor.execute("UPDATE setlist_songs SET play_order = ? WHERE id = ? AND setlist_id = ?", (index + 1, song_id, setlist_id))
    conn.commit()
    conn.close()
    return {"message": "reordered"}