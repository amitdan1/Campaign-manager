"""
APScheduler-based task scheduler for automated marketing operations.
Handles: daily metrics pull, lead re-scoring, weekly strategy cycle.

Usage:
    from services.scheduler import init_scheduler
    init_scheduler(app, orchestrator)
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("services.scheduler")

_scheduler: BackgroundScheduler = None


def init_scheduler(app, orchestrator) -> BackgroundScheduler:
    """Initialize and start the background scheduler."""
    global _scheduler

    if _scheduler and _scheduler.running:
        logger.info("Scheduler already running, skipping init")
        return _scheduler

    _scheduler = BackgroundScheduler(daemon=True)

    # 1. Daily metrics pull (every day at 06:00)
    def daily_metrics_pull():
        with app.app_context():
            logger.info("Scheduled: daily metrics pull")
            try:
                orchestrator.campaign_tracking.run()
            except Exception as e:
                logger.error(f"Scheduled metrics pull failed: {e}")

    _scheduler.add_job(
        daily_metrics_pull,
        CronTrigger(hour=6, minute=0),
        id="daily_metrics_pull",
        replace_existing=True,
    )

    # 2. Daily lead re-scoring (every day at 07:00)
    def daily_lead_rescoring():
        with app.app_context():
            logger.info("Scheduled: daily lead re-scoring")
            try:
                orchestrator.lead_scoring.run()
            except Exception as e:
                logger.error(f"Scheduled lead re-scoring failed: {e}")

    _scheduler.add_job(
        daily_lead_rescoring,
        CronTrigger(hour=7, minute=0),
        id="daily_lead_rescoring",
        replace_existing=True,
    )

    # 3. Weekly strategy cycle (every Sunday at 08:00)
    def weekly_strategy_cycle():
        with app.app_context():
            logger.info("Scheduled: weekly strategy cycle")
            try:
                from agents.execution_pipeline import ExecutionPipeline
                pipeline = ExecutionPipeline(orchestrator)
                pipeline.run_weekly_cycle()
            except Exception as e:
                logger.error(f"Scheduled weekly strategy cycle failed: {e}")

    _scheduler.add_job(
        weekly_strategy_cycle,
        CronTrigger(day_of_week="sun", hour=8, minute=0),
        id="weekly_strategy_cycle",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Background scheduler started with 3 jobs")
    return _scheduler


def get_scheduler_status() -> dict:
    """Return status of the scheduler and its jobs."""
    if not _scheduler:
        return {"running": False, "jobs": []}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {"running": _scheduler.running, "jobs": jobs}
