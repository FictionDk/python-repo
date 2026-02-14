"""
Automated Task Scheduler for GitLab Operations

This module provides scheduled task execution for:
- Weekly: analyze_development_progress (every Monday at 4:00 AM)
- Daily: clone_all_commit, sync_issue_by_commit, clone_snapshot (every day at 1:00 AM)

Usage:
    # Run the scheduler (continuous execution)
    python task.py
    
    # Or import and run specific functions
    from task import run_daily_tasks, run_weekly_tasks
    run_daily_tasks()
"""

import schedule
import time
from datetime import datetime
import logging
import signal

from manage_commit import clone_all_commit, sync_issue_by_commit, analyze_development_progress
from manage_issue import clone_snapshot
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks for GitLab operations"""
    
    def __init__(self, project_id: int = None):
        """
        Initialize task scheduler
        
        Args:
            project_id: Project ID for issue-related tasks (default: None)
        """
        self.project_id = project_id
        self.config = Config()
        self.running = True
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run_clone_all_commit(self):
        """Execute clone_all_commit task"""
        task_name = "clone_all_commit"
        logger.info(f"🚀 Starting task: {task_name}")
        try:
            start_time = datetime.now()
            result = clone_all_commit(project_id=None)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"✅ {task_name} completed successfully in {duration:.2f}s")
            logger.info(f"   Result: {result}")
        except Exception as e:
            logger.error(f"❌ {task_name} failed: {e}", exc_info=True)
    
    def run_sync_issue_by_commit(self):
        """Execute sync_issue_by_commit task"""
        task_name = "sync_issue_by_commit"
        logger.info(f"🚀 Starting task: {task_name}")
        try:
            start_time = datetime.now()
            result = sync_issue_by_commit()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"✅ {task_name} completed successfully in {duration:.2f}s")
            logger.info(f"   Processed: {result.get('success', 0)}/{result.get('total_issues_processed', 0)} issues")
        except Exception as e:
            logger.error(f"❌ {task_name} failed: {e}", exc_info=True)
    
    def run_clone_snapshot(self):
        """Execute clone_snapshot task"""
        task_name = "clone_snapshot"
        logger.info(f"🚀 Starting task: {task_name}")
        try:
            start_time = datetime.now()
            if self.project_id:
                result = clone_snapshot(self.project_id)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"✅ {task_name} completed successfully in {duration:.2f}s")
                logger.info(f"   Total issues: {result.get('issue_total', 0)}, New: {result.get('issue_main_new', 0)}")
            else:
                logger.warning(f"⚠️  {task_name} skipped: project_id not configured")
        except Exception as e:
            logger.error(f"❌ {task_name} failed: {e}", exc_info=True)
    
    def run_analyze_development_progress(self):
        """Execute analyze_development_progress task"""
        task_name = "analyze_development_progress"
        logger.info(f"🚀 Starting task: {task_name}")
        try:
            start_time = datetime.now()
            report = analyze_development_progress()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"✅ {task_name} completed successfully in {duration:.2f}s")
            logger.info(f"📊 Weekly Report: {report}")
        except Exception as e:
            logger.error(f"❌ {task_name} failed: {e}", exc_info=True)
    
    def run_daily_tasks(self):
        """Execute all daily tasks (clone_all_commit, sync_issue_by_commit, clone_snapshot)"""
        logger.info("=" * 80)
        logger.info("🌅 Starting daily tasks execution")
        logger.info("=" * 80)
        
        # Task 1: Clone all commits
        self.run_clone_all_commit()
        logger.info("-" * 80)
        
        # Task 2: Sync issues by commit
        self.run_sync_issue_by_commit()
        logger.info("-" * 80)
        
        # Task 3: Clone snapshot (if project_id is configured)
        self.run_clone_snapshot()
        logger.info("-" * 80)
        
        logger.info("🌙 Daily tasks execution completed")
        logger.info("=" * 80)
    
    def run_weekly_tasks(self):
        """Execute weekly task (analyze_development_progress)"""
        logger.info("=" * 80)
        logger.info("📅 Starting weekly tasks execution")
        logger.info("=" * 80)
        
        # Task: Analyze development progress
        self.run_analyze_development_progress()
        
        logger.info("📅 Weekly tasks execution completed")
        logger.info("=" * 80)
    
    def setup_schedule(self):
        """Set up the task schedule"""
        logger.info("⏰ Setting up task scheduler...")
        
        # Daily tasks at 1:00 AM
        schedule.every().day.at("01:00").do(self.run_daily_tasks)
        logger.info("   Scheduled: Daily tasks at 01:00 AM")
        
        # Weekly task (Monday at 4:00 AM)
        schedule.every().monday.at("04:00").do(self.run_weekly_tasks)
        logger.info("   Scheduled: Weekly task (Monday) at 04:00 AM")
        
        logger.info("✅ Task scheduler ready")
    
    def run(self):
        """Run the scheduler continuously"""
        logger.info("🎯 Starting task scheduler...")
        logger.info(f"   Press Ctrl+C to stop")
        
        self.setup_schedule()
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}", exc_info=True)
        finally:
            logger.info("👋 Scheduler shutdown complete")


def run_daily_tasks(project_id: int = None):
    """
    Convenience function: Run all daily tasks immediately
    
    Args:
        project_id: Project ID for clone_snapshot task
    """
    scheduler = TaskScheduler(project_id=project_id)
    scheduler.run_daily_tasks()


def run_weekly_tasks():
    """Convenience function: Run weekly task immediately"""
    scheduler = TaskScheduler()
    scheduler.run_weekly_tasks()


def start_scheduler(project_id: int = None):
    """
    Convenience function: Start the automated scheduler
    
    Args:
        project_id: Project ID for clone_snapshot task
    """
    scheduler = TaskScheduler(project_id=project_id)
    scheduler.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GitLab Task Scheduler')
    parser.add_argument(
        '--mode',
        choices=['scheduler', 'daily', 'weekly'],
        default='scheduler',
        help='Execution mode: scheduler (continuous), daily (run once), weekly (run once)'
    )
    parser.add_argument(
        '--project-id',
        type=int,
        default=None,
        help='Project ID for snapshot tasks'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'scheduler':
        logger.info("🚀 Starting in scheduler mode (continuous execution)")
        start_scheduler(project_id=args.project_id)
    elif args.mode == 'daily':
        logger.info("🚀 Starting in daily mode (execute daily tasks once)")
        run_daily_tasks(project_id=args.project_id)
    elif args.mode == 'weekly':
        logger.info("🚀 Starting in weekly mode (execute weekly task once)")
        run_weekly_tasks()
