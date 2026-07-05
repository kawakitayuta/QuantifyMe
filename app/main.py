from fastapi import FastAPI, Depends, Header, HTTPException
import os
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from app.database import get_db, engine
from app.models import Base, HealthLog
from app.schemas import HealthLogIn, HealthLogOut
from app.analytics import router as analytics_router

app = FastAPI(title="QuantifyMe API")
app.include_router(analytics_router)
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")

API_KEY = os.getenv("API_KEY")

def verify_api_key(x_api_key: str = Header(None)):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/health-log", response_model=HealthLogOut)
async def upsert_log(entry: HealthLogIn, db: AsyncSession = Depends(get_db), _: None = Depends(verify_api_key)):
    data = entry.model_dump(exclude_unset=True)
    stmt = insert(HealthLog).values(**data)
    update_fields = {k: v for k, v in data.items() if k != "date"}
    stmt = stmt.on_conflict_do_update(
        index_elements=["date"],
        set_=update_fields
    ).returning(HealthLog)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()

@app.get("/health-log", response_model=list[HealthLogOut])
async def list_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HealthLog).order_by(HealthLog.date.desc()))
    return result.scalars().all()
