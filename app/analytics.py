from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/daily-comparison")
async def daily_comparison(user_name: str = "yuta", db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT
            date,
            steps,
            LAG(steps) OVER (ORDER BY date) AS previous_day_steps,
            steps - LAG(steps) OVER (ORDER BY date) AS diff
        FROM health_log
        WHERE user_name = :user_name
        ORDER BY date
    """)
    result = await db.execute(query, {"user_name": user_name})
    return result.mappings().all()


@router.get("/7day-average")
async def seven_day_average(user_name: str = "yuta", db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT
            date,
            steps,
            ROUND(AVG(steps) OVER (
                ORDER BY date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 0) AS avg_7days
        FROM health_log
        WHERE user_name = :user_name
        ORDER BY date
    """)
    result = await db.execute(query, {"user_name": user_name})
    return result.mappings().all()


@router.get("/weekday-average")
async def weekday_average(user_name: str = "yuta", db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT
            TO_CHAR(date, 'Day') AS day_of_week,
            ROUND(AVG(steps), 0) AS avg_steps
        FROM health_log
        WHERE user_name = :user_name
        GROUP BY TO_CHAR(date, 'Day')
        ORDER BY avg_steps DESC
    """)
    result = await db.execute(query, {"user_name": user_name})
    return result.mappings().all()


@router.get("/streaks")
async def streaks(user_name: str = "yuta", db: AsyncSession = Depends(get_db)):
    query = text("""
        WITH achieved AS (
            SELECT
                date,
                steps,
                date - (ROW_NUMBER() OVER (ORDER BY date))::int AS grp
            FROM health_log
            WHERE steps >= 10000 AND user_name = :user_name
        )
        SELECT
            grp,
            MIN(date) AS streak_start,
            MAX(date) AS streak_end,
            COUNT(*) AS streak_length
        FROM achieved
        GROUP BY grp
        ORDER BY streak_length DESC
    """)
    result = await db.execute(query, {"user_name": user_name})
    return result.mappings().all()


@router.get("/monthly-ranking")
async def monthly_ranking(user_name: str = "yuta", db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT
            date,
            steps,
            ROW_NUMBER() OVER (
                PARTITION BY DATE_TRUNC('month', date)
                ORDER BY steps DESC
            ) AS rank_in_month
        FROM health_log
        WHERE user_name = :user_name
        ORDER BY date
    """)
    result = await db.execute(query, {"user_name": user_name})
    return result.mappings().all()

@router.get("/today-ranking")
async def today_ranking(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT
            user_name,
            steps,
            RANK() OVER (ORDER BY steps DESC) AS rank
        FROM health_log
        WHERE date = CURRENT_DATE
        ORDER BY steps DESC
    """)
    result = await db.execute(query)
    return result.mappings().all()


@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT user_name FROM (
            SELECT DISTINCT user_name FROM health_log
        ) AS sub
        ORDER BY CASE WHEN user_name = 'yuta' THEN 0 ELSE 1 END, user_name
    """)
    result = await db.execute(query)
    return [row[0] for row in result.all()]
