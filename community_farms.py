"""Local prototype crop journal; anonymous public output is aggregate and opt-in only.

IMPORTANT: SQLite is shared only by users accessing the SAME deployed application
instance. No global federation, account verification, or production-grade privacy.
"""
from datetime import date
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import math
import sqlite3

DB = Path(__file__).with_name('farmer_journal.db')
GRID_DEGREES = 0.02


def _connect(path=None):
    conn = sqlite3.connect(str(path or DB), timeout=10)
    conn.execute('''CREATE TABLE IF NOT EXISTS plantings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_key TEXT NOT NULL,
        crop TEXT NOT NULL,
        sowing_date TEXT NOT NULL,
        harvest_date TEXT,
        irrigation_date TEXT,
        irrigation_method TEXT,
        farmer_notes TEXT,
        exact_lat REAL NOT NULL,
        exact_lon REAL NOT NULL,
        grid_lat REAL NOT NULL,
        grid_lon REAL NOT NULL,
        share_crop INTEGER NOT NULL DEFAULT 0
    )''')
    conn.commit()
    return conn


def _owner_key(email):
    return sha256(email.strip().lower().encode()).hexdigest()


def _grid(lat, lon):
    return (round(math.floor(lat / GRID_DEGREES) * GRID_DEGREES + GRID_DEGREES / 2, 4),
            round(math.floor(lon / GRID_DEGREES) * GRID_DEGREES + GRID_DEGREES / 2, 4))


def save_planting(email, crop, sowing_date, lat, lon, harvest_date=None,
                  irrigation_date=None, irrigation_method='', farmer_notes='',
                  share_crop=False, db_path=None):
    if not email:
        raise ValueError('Sign in to save a planting.')
    if not crop or len(crop.strip()) > 80:
        raise ValueError('Crop name is empty or too long.')
    if not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180):
        raise ValueError('Invalid coordinates.')
    if len(farmer_notes) > 500:
        raise ValueError('Notes must be at most 500 characters.')
    grid_lat, grid_lon = _grid(float(lat), float(lon))
    with closing(_connect(db_path)) as conn, conn:
        conn.execute('''INSERT INTO plantings (
            owner_key,crop,sowing_date,harvest_date,irrigation_date,irrigation_method,farmer_notes,
            exact_lat,exact_lon,grid_lat,grid_lon,share_crop
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', (
            _owner_key(email), crop.strip(), str(sowing_date),
            str(harvest_date) if harvest_date else None,
            str(irrigation_date) if irrigation_date else None,
            irrigation_method, farmer_notes, float(lat), float(lon),grid_lat,grid_lon,int(bool(share_crop))))


def my_plantings(email, db_path=None):
    if not email:
        return []
    with closing(_connect(db_path)) as conn, conn:
        rows = conn.execute('''SELECT id,crop,sowing_date,harvest_date,irrigation_date,
                                irrigation_method,farmer_notes,share_crop FROM plantings
                                WHERE owner_key=? ORDER BY id DESC LIMIT 50''', (_owner_key(email),)).fetchall()
    return [dict(zip(('id','Crop','Sowing','Harvest','Irrigation','Method','Private notes','Shared'), row)) for row in rows]


def update_share(email, record_id, share, db_path=None):
    with closing(_connect(db_path)) as conn, conn:
        conn.execute('UPDATE plantings SET share_crop=? WHERE id=? AND owner_key=?',
                     (int(bool(share)), int(record_id), _owner_key(email)))


def delete_record(email, record_id, db_path=None):
    with closing(_connect(db_path)) as conn, conn:
        conn.execute('DELETE FROM plantings WHERE id=? AND owner_key=?', (int(record_id), _owner_key(email)))


def _distance_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2-p1, math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371 * 2 * math.asin(min(1.0, math.sqrt(a)))


def nearby_crop_totals(latitude, longitude, db_path=None, radius_km=5, min_farms=3):
    """Only share-enabled accounts; suppress crops contributed by <3 unique accounts.

    No exact coordinates, individual farms, identities, notes, or activity dates returned.
    """
    with closing(_connect(db_path)) as conn, conn:
        rows = conn.execute('''SELECT crop,owner_key,grid_lat,grid_lon FROM plantings
                               WHERE share_crop=1''').fetchall()
    crop_to_owners = {}
    for crop, owner, glat, glon in rows:
        if _distance_km(latitude, longitude, glat, glon) <= radius_km:
            crop_to_owners.setdefault(crop, set()).add(owner)
    return [{'Crop': crop, 'Sharing farms': len(owners)}
            for crop, owners in sorted(crop_to_owners.items()) if len(owners) >= min_farms]
