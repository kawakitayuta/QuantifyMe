from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from app.database import get_db, engine
from app.models import Base, HealthLog
from app.schemas import HealthLogIn, HealthLogOut

app = FastAPI(title="QuantifyMe API")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/health-log", response_model=HealthLogOut)
async def upsert_log(entry: HealthLogIn, db: AsyncSession = Depends(get_db)):
    stmt = insert(HealthLog).values(**entry.model_dump())
    stmt = stmt.on_conflict_do_update(
        index_elements=["date"],
        set_={k: v for k, v in entry.model_dump().items() if k != "date"}
    ).returning(HealthLog)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()

@app.get("/health-log", response_model=list[HealthLogOut])
async def list_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HealthLog).order_by(HealthLog.date.desc()))
    return result.scalars().all()
