from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2  # SQLiteの代わりにpsycopg2（PostgreSQL用ツール）をインポート
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================================
# 【重要】ここにパスワードを書き換えたSupabaseの接続用URL（URI）を貼り付けてください
# =========================================================================
DATABASE_URL = "postgresql://postgres:hamaniku23-1@db.doryrnzteamqzrfmgtab.supabase.co:5432/postgres"

def get_db_connection():
    # クラウドデータベースへの接続パイプを開く関数
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 最初のバンドテストデータを投入（重複を避ける設定）
    test_bands = ["ずっと珠でいいのに。", "ヨシムラ", "メスの極み綾部。"]
    for band in test_bands:
        cursor.execute("INSERT INTO bands (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (band,))
            
    # クラウド側が完全に空っぽの場合のみ、初期データを流し込む
    cursor.execute("SELECT count(*) FROM events;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id FROM bands WHERE name = %s;", ('ずっと珠でいいのに。',))
        band_row = cursor.fetchone()
        if band_row:
            band_id = band_row[0]
            
            # イベントデータの投入
            cursor.execute("INSERT INTO events (band_id, date, location) VALUES (%s, %s, %s);", (band_id, "2024-05-01", "ホンダ楽器"))
            cursor.execute("INSERT INTO events (band_id, date, location) VALUES (%s, %s, %s);", (band_id, "2024-06-10", "RSEスタジオ"))

            # 独立した「セットリスト」の作成
            cursor.execute("INSERT INTO setlists (band_id, title) VALUES (%s, %s) RETURNING id;", (band_id, "基本セットリスト"))
            setlist_id = cursor.fetchone()[0]

            # セットリストの中に4曲を登録
            songs_data = [
                (setlist_id, 1, "秒針を噛む", ""),
                (setlist_id, 2, "低血ボルト", ""),
                (setlist_id, 3, "ハゼ馳せる果てるまで", ""),
                (setlist_id, 4, "勘冴えて悔しいわ", "イントロでオーバードライブを踏む")
            ]
            for song in songs_data:
                cursor.execute("INSERT INTO setlist_songs (setlist_id, play_order, song_name, gear_note) VALUES (%s, %s, %s, %s);", song)

    conn.commit()
    conn.close()

# アプリ起動時に初期データをチェック・投入する
init_db()

# --- APIエンドポイント（読み取り） ---

@app.get("/")
def read_root(): 
    return {"message": "BandVault API (Connected to Supabase)"}

@app.get("/api/bands")
def get_bands():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM bands ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in rows]

@app.get("/api/bands/{band_id}")
def get_band(band_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM bands WHERE id = %s;", (band_id,))
    row = cursor.fetchone()
    conn.close()
    return {"id": row[0], "name": row[1]} if row else {"error": "Band not found"}

@app.get("/api/bands/{band_id}/events")
def get_events(band_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, location FROM events WHERE band_id = %s ORDER BY date DESC;", (band_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "date": row[1], "location": row[2]} for row in rows]

@app.get("/api/bands/{band_id}/setlists")
def get_setlists(band_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM setlists WHERE band_id = %s ORDER BY id ASC;", (band_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "title": row[1]} for row in rows]

@app.get("/api/setlists/{setlist_id}/songs")
def get_setlist_songs(setlist_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, play_order, song_name, gear_note FROM setlist_songs WHERE setlist_id = %s ORDER BY play_order ASC;", (setlist_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "play_order": row[1], "song_name": row[2], "gear_note": row[3]} for row in rows]


# --- APIエンドポイント（書き込み・変更・削除） ---

class BandCreate(BaseModel): name: str
class EventCreate(BaseModel): date: str; location: str
class SetlistCreate(BaseModel): title: str
class SongCreate(BaseModel): song_name: str; gear_note: str
class ReorderData(BaseModel): song_ids: list[int]

@app.post("/api/bands")
def create_band(band: BandCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bands (name) VALUES (%s) RETURNING id;", (band.name,))
        new_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return {"id": new_id, "name": band.name}
    except Exception:
        conn.close()
        return {"error": "already exists"}

@app.post("/api/bands/{band_id}/events")
def create_event(band_id: int, event: EventCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (band_id, date, location) VALUES (%s, %s, %s) RETURNING id;", (band_id, event.date, event.location))
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": new_id, "date": event.date, "location": event.location}

@app.post("/api/bands/{band_id}/setlists")
def create_setlist(band_id: int, setlist: SetlistCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO setlists (band_id, title) VALUES (%s, %s) RETURNING id;", (band_id, setlist.title))
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": new_id, "title": setlist.title}

@app.post("/api/setlists/{setlist_id}/songs")
def create_song(setlist_id: int, song: SongCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM setlist_songs WHERE setlist_id = %s;", (setlist_id,))
    next_order = cursor.fetchone()[0] + 1
    cursor.execute("INSERT INTO setlist_songs (setlist_id, play_order, song_name, gear_note) VALUES (%s, %s, %s, %s) RETURNING id;", 
                   (setlist_id, next_order, song.song_name, song.gear_note))
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": new_id, "play_order": next_order, "song_name": song.song_name, "gear_note": song.gear_note}

@app.delete("/api/bands/{band_id}")
def delete_band(band_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bands WHERE id = %s;", (band_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = %s;", (event_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

@app.delete("/api/setlists/{setlist_id}")
def delete_setlist(setlist_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM setlists WHERE id = %s;", (setlist_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

@app.delete("/api/songs/{song_id}")
def delete_song(song_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM setlist_songs WHERE id = %s;", (song_id,))
    conn.commit()
    conn.close()
    return {"message": "deleted"}

@app.put("/api/setlists/{setlist_id}/reorder")
def reorder_songs(setlist_id: int, data: ReorderData):
    conn = get_db_connection()
    cursor = conn.cursor()
    for index, song_id in enumerate(data.song_ids):
        cursor.execute("UPDATE setlist_songs SET play_order = %s WHERE id = %s AND setlist_id = %s;", (index + 1, song_id, setlist_id))
    conn.commit()
    conn.close()
    return {"message": "reordered"}