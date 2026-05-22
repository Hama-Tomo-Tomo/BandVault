import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom'

// 共通のボタン用スタイル
const deleteBtnStyle = { backgroundColor: '#ff4d4f', color: '#fff', border: 'none', borderRadius: '4px', padding: '6px 12px', cursor: 'pointer', fontSize: '14px', fontWeight: 'bold' }
const moveBtnStyle = { backgroundColor: '#e0e0e0', color: '#333', border: 'none', borderRadius: '4px', padding: '6px 12px', cursor: 'pointer', fontSize: '14px', fontWeight: 'bold' }

function BandList() {
  const [bands, setBands] = useState([])
  const [newBandName, setNewBandName] = useState('')
  const fetchBands = () => { fetch('http://127.0.0.1:8000/api/bands').then(res => res.json()).then(data => setBands(data)) }
  useEffect(() => { fetchBands() }, [])
  const handleAddBand = (e) => {
    e.preventDefault()
    if (!newBandName) return
    fetch('http://127.0.0.1:8000/api/bands', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: newBandName }) }).then(() => { setNewBandName(''); fetchBands(); })
  }
  const handleDeleteBand = (id) => {
    if (window.confirm("本当にこのバンドを削除しますか？")) { fetch(`http://127.0.0.1:8000/api/bands/${id}`, { method: 'DELETE' }).then(() => fetchBands()) }
  }
  return (
    <div>
      <h2 style={{ borderBottom: '2px solid #333', paddingBottom: '10px' }}>マイバンド一覧</h2>
      <form onSubmit={handleAddBand} style={{ backgroundColor: '#f0f7ff', padding: '20px', borderRadius: '8px', marginBottom: '30px', display: 'flex', gap: '10px' }}>
        <input type="text" placeholder="新しいバンド名" value={newBandName} onChange={(e) => setNewBandName(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', flex: 1 }} />
        <button type="submit" style={{ padding: '8px 16px', backgroundColor: '#1565c0', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>＋ バンド追加</button>
      </form>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
        {bands.map(band => (
          <div key={band.id} style={{ border: '1px solid #e0e0e0', borderRadius: '12px', padding: '20px', backgroundColor: '#ffffff', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Link to={`/bands/${band.id}`} style={{ textDecoration: 'none', color: '#333', flex: 1 }}><h3 style={{ margin: 0, fontSize: '18px' }}>{band.name}</h3></Link>
            <button onClick={() => handleDeleteBand(band.id)} style={deleteBtnStyle}>削除</button>
          </div>
        ))}
      </div>
    </div>
  )
}

function BandMenu() {
  const { id } = useParams()
  const [band, setBand] = useState({})
  useEffect(() => { fetch(`http://127.0.0.1:8000/api/bands/${id}`).then(res => res.json()).then(data => setBand(data)) }, [id])
  return (
    <div>
      <Link to="/" style={{ color: '#0066cc', textDecoration: 'none' }}>← バンド一覧に戻る</Link>
      <h2 style={{ borderBottom: '2px solid #333', paddingBottom: '10px', marginTop: '20px' }}>{band.name} の管理メニュー</h2>
      <div style={{ display: 'flex', gap: '20px', marginTop: '30px' }}>
        <Link to={`/bands/${id}/events`} style={{ flex: 1, textDecoration: 'none' }}><div style={{ backgroundColor: '#e3f2fd', padding: '40px 20px', borderRadius: '12px', textAlign: 'center', color: '#1565c0', fontWeight: 'bold', fontSize: '18px', transition: '0.2s', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>📅 ライブ・練習の日程</div></Link>
        <Link to={`/bands/${id}/setlists`} style={{ flex: 1, textDecoration: 'none' }}><div style={{ backgroundColor: '#f3e5f5', padding: '40px 20px', borderRadius: '12px', textAlign: 'center', color: '#6a1b9a', fontWeight: 'bold', fontSize: '18px', transition: '0.2s', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>🎸 セットリスト</div></Link>
      </div>
    </div>
  )
}

function EventList() {
  const { id } = useParams()
  const [events, setEvents] = useState([])
  const [newDate, setNewDate] = useState('')
  const [newLocation, setNewLocation] = useState('')
  const fetchEvents = () => { fetch(`http://127.0.0.1:8000/api/bands/${id}/events`).then(res => res.json()).then(data => setEvents(data)) }
  useEffect(() => { fetchEvents() }, [id])
  const handleAddEvent = (e) => {
    e.preventDefault()
    if (!newDate || !newLocation) return
    fetch(`http://127.0.0.1:8000/api/bands/${id}/events`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ date: newDate, location: newLocation }) }).then(() => { setNewDate(''); setNewLocation(''); fetchEvents(); })
  }
  const handleDeleteEvent = (eventId) => {
    if (window.confirm("この予定を削除しますか？")) { fetch(`http://127.0.0.1:8000/api/events/${eventId}`, { method: 'DELETE' }).then(() => fetchEvents()) }
  }
  return (
    <div>
      <Link to={`/bands/${id}`} style={{ color: '#0066cc', textDecoration: 'none' }}>← メニューに戻る</Link>
      <h2 style={{ borderBottom: '2px solid #333', paddingBottom: '10px', marginTop: '20px' }}>イベント履歴</h2>
      <form onSubmit={handleAddEvent} style={{ backgroundColor: '#f0f7ff', padding: '20px', borderRadius: '8px', marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <input type="date" value={newDate} onChange={(e) => setNewDate(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />
        <input type="text" placeholder="場所" value={newLocation} onChange={(e) => setNewLocation(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', flex: 1 }} />
        <button type="submit" style={{ padding: '8px 16px', backgroundColor: '#1565c0', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>＋ 追加</button>
      </form>
      <div>
        {events.map(event => (
          <div key={event.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '4px solid #1565c0', padding: '15px', marginBottom: '15px', backgroundColor: '#f9f9f9', borderRadius: '0 8px 8px 0' }}>
            <div><h3 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>{event.date}</h3><p style={{ margin: 0, color: '#666' }}>📍 {event.location}</p></div>
            <button onClick={() => handleDeleteEvent(event.id)} style={deleteBtnStyle}>削除</button>
          </div>
        ))}
      </div>
    </div>
  )
}

function SetlistList() {
  const { id } = useParams()
  const [setlists, setSetlists] = useState([])
  const [newTitle, setNewTitle] = useState('')
  const fetchSetlists = () => { fetch(`http://127.0.0.1:8000/api/bands/${id}/setlists`).then(res => res.json()).then(data => setSetlists(data)) }
  useEffect(() => { fetchSetlists() }, [id])
  const handleAddSetlist = (e) => {
    e.preventDefault()
    if (!newTitle) return
    fetch(`http://127.0.0.1:8000/api/bands/${id}/setlists`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: newTitle }) }).then(() => { setNewTitle(''); fetchSetlists(); })
  }
  const handleDeleteSetlist = (setlistId) => {
    if (window.confirm("このセットリストを削除しますか？")) { fetch(`http://127.0.0.1:8000/api/setlists/${setlistId}`, { method: 'DELETE' }).then(() => fetchSetlists()) }
  }
  return (
    <div>
      <Link to={`/bands/${id}`} style={{ color: '#0066cc', textDecoration: 'none' }}>← メニューに戻る</Link>
      <h2 style={{ borderBottom: '2px solid #333', paddingBottom: '10px', marginTop: '20px' }}>セットリスト一覧</h2>
      <form onSubmit={handleAddSetlist} style={{ backgroundColor: '#fdf4f5', padding: '20px', borderRadius: '8px', marginBottom: '20px', display: 'flex', gap: '10px' }}>
        <input type="text" placeholder="セットリスト名" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', flex: 1 }} />
        <button type="submit" style={{ padding: '8px 16px', backgroundColor: '#6a1b9a', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>＋ 追加</button>
      </form>
      <div>
        {setlists.map(setlist => (
          <div key={setlist.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #e0e0e0', padding: '20px', marginBottom: '15px', borderRadius: '8px', backgroundColor: '#fff' }}>
            <Link to={`/setlists/${setlist.id}`} style={{ textDecoration: 'none', color: '#333', flex: 1 }}><h3 style={{ margin: 0, fontSize: '18px' }}>📋 {setlist.title}</h3></Link>
            <button onClick={() => handleDeleteSetlist(setlist.id)} style={deleteBtnStyle}>削除</button>
          </div>
        ))}
      </div>
    </div>
  )
}

// 5. セットリスト詳細画面（★ここに曲順変更と削除機能を追加しました）
function SetlistDetail() {
  const { setId } = useParams()
  const [songs, setSongs] = useState([])
  const [songName, setSongName] = useState('')
  const [gearNote, setGearNote] = useState('')

  const fetchSongs = () => { fetch(`http://127.0.0.1:8000/api/setlists/${setId}/songs`).then(res => res.json()).then(data => setSongs(data)) }
  useEffect(() => { fetchSongs() }, [setId])

  const handleAddSong = (e) => {
    e.preventDefault()
    if (!songName) return
    fetch(`http://127.0.0.1:8000/api/setlists/${setId}/songs`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ song_name: songName, gear_note: gearNote }) }).then(() => { setSongName(''); setGearNote(''); fetchSongs(); })
  }

  // ★ 曲の削除機能
  const handleDeleteSong = (songId) => {
    if (window.confirm("この曲をセットリストから外しますか？")) {
      fetch(`http://127.0.0.1:8000/api/songs/${songId}`, { method: 'DELETE' }).then(() => fetchSongs())
    }
  }

  // ★ 曲の順番入れ替え機能
  const moveSong = (index, direction) => {
    const newSongs = [...songs];
    if (direction === 'up' && index > 0) {
      const temp = newSongs[index];
      newSongs[index] = newSongs[index - 1];
      newSongs[index - 1] = temp;
    } else if (direction === 'down' && index < newSongs.length - 1) {
      const temp = newSongs[index];
      newSongs[index] = newSongs[index + 1];
      newSongs[index + 1] = temp;
    } else {
      return;
    }

    // 画面の見た目を先に更新
    setSongs(newSongs);

    // バックエンドに新しい順番のIDリストを送って保存させる
    const songIds = newSongs.map(s => s.id);
    fetch(`http://127.0.0.1:8000/api/setlists/${setId}/reorder`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ song_ids: songIds })
    }).then(() => fetchSongs()); // 保存完了後に最新データを再取得
  }

  return (
    <div>
      <button onClick={() => window.history.back()} style={{ background: 'none', border: 'none', color: '#0066cc', cursor: 'pointer', padding: 0, fontSize: '16px' }}>← 一覧に戻る</button>
      <h2 style={{ borderBottom: '2px solid #333', paddingBottom: '10px', marginTop: '20px' }}>セットリスト詳細</h2>
      
      <form onSubmit={handleAddSong} style={{ backgroundColor: '#f9f9f9', padding: '20px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #ddd' }}>
        <input type="text" placeholder="曲名（必須）" value={songName} onChange={(e) => setSongName(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', width: '100%', marginBottom: '10px', boxSizing: 'border-box' }} />
        <input type="text" placeholder="機材メモ（任意）" value={gearNote} onChange={(e) => setGearNote(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', width: '100%', marginBottom: '10px', boxSizing: 'border-box' }} />
        <button type="submit" style={{ padding: '8px 16px', backgroundColor: '#333', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', width: '100%', fontWeight: 'bold' }}>＋ 追加</button>
      </form>

      <div>
        {songs.length === 0 ? <p style={{ color: '#666' }}>曲が登録されていません。</p> : songs.map((song, index) => (
          <div key={song.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', border: '1px solid #ddd', padding: '15px', marginBottom: '15px', borderRadius: '8px', backgroundColor: '#fafafa' }}>
            <div style={{ flex: 1 }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '18px' }}>{index + 1}. {song.song_name}</h3>
              {song.gear_note && <div style={{ backgroundColor: '#fff3e0', padding: '10px', borderRadius: '4px', borderLeft: '4px solid #ff9800', fontSize: '14px', color: '#e65100', marginRight: '10px' }}><strong>機材メモ:</strong> {song.gear_note}</div>}
            </div>
            {/* 上下移動・削除ボタン群 */}
            <div style={{ display: 'flex', gap: '5px' }}>
              <button onClick={() => moveSong(index, 'up')} style={{ ...moveBtnStyle, visibility: index === 0 ? 'hidden' : 'visible' }}>↑</button>
              <button onClick={() => moveSong(index, 'down')} style={{ ...moveBtnStyle, visibility: index === songs.length - 1 ? 'hidden' : 'visible' }}>↓</button>
              <button onClick={() => handleDeleteSong(song.id)} style={{ ...deleteBtnStyle, marginLeft: '10px' }}>削除</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: '40px 20px', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
        <Routes>
          <Route path="/" element={<BandList />} />
          <Route path="/bands/:id" element={<BandMenu />} />
          <Route path="/bands/:id/events" element={<EventList />} />
          <Route path="/bands/:id/setlists" element={<SetlistList />} />
          <Route path="/setlists/:setId" element={<SetlistDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App