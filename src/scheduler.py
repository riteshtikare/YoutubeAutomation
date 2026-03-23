"""
scheduler.py — runs the pipeline automatically on a schedule.
Default: once per day at 10:00 AM local time.

Usage:
    python scheduler.py                  # run with defaults
    python scheduler.py --time 14:30     # run daily at 2:30 PM
    python scheduler.py --interval 12    # run every 12 hours
"""

import schedule
import time
import logging
import argparse
from pipeline import run_pipeline
from config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def job():
    log.info("⏰  Scheduler triggered — starting pipeline …")
    try:
        cfg = Settings()
        summary = run_pipeline(niche=cfg.DEFAULT_NICHE)
        log.info(f"✅  Done! → {summary.get('youtube_url')}")
    except Exception as e:
        log.error(f"❌  Pipeline failed: {e}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--time", default="10:00", help="Daily run time HH:MM (default 10:00)")
    parser.add_argument("--interval", type=int, default=None, help="Run every N hours instead")
    args = parser.parse_args()

    if args.interval:
        log.info(f"📅  Scheduling pipeline every {args.interval} hours.")
        schedule.every(args.interval).hours.do(job)
    else:
        log.info(f"📅  Scheduling pipeline daily at {args.time}.")
        schedule.every().day.at(args.time).do(job)

    log.info("🚀  Scheduler running — press Ctrl+C to stop.")
    job()   # run immediately on start

    while True:
        schedule.run_pending()
        time.sleep(60)
