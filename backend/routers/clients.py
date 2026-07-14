from fastapi import APIRouter, HTTPException
from ..database import get_conn
from ..models import ClientCreate, ClientUpdate

router = APIRouter()


@router.get("/")
def list_clients():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM clients ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/")
def create_client(client: ClientCreate):
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO clients
           (name, niche, description, instagram, tiktok, facebook, youtube, website, brand_tone, target_audience)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (client.name, client.niche, client.description, client.instagram, client.tiktok,
         client.facebook, client.youtube, client.website, client.brand_tone, client.target_audience),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM clients WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@router.get("/{client_id}")
def get_client(client_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return dict(row)


@router.put("/{client_id}")
def update_client(client_id: int, client: ClientUpdate):
    conn = get_conn()
    conn.execute(
        """UPDATE clients SET name=?, niche=?, description=?, instagram=?, tiktok=?, facebook=?,
           youtube=?, website=?, brand_tone=?, target_audience=?, active=? WHERE id=?""",
        (client.name, client.niche, client.description, client.instagram, client.tiktok,
         client.facebook, client.youtube, client.website, client.brand_tone, client.target_audience,
         client.active, client_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    conn.close()
    return dict(row)


@router.delete("/{client_id}")
def delete_client(client_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return {"ok": True}
