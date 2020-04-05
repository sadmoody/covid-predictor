from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from core.tasks import update_confirmed_stats, update_death_stats

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_confirmed_stats, max_instances=1, trigger='cron', minute='*/1')
    scheduler.add_job(update_death_stats, max_instances=1, trigger='cron', minute='*/1')
    scheduler.start()