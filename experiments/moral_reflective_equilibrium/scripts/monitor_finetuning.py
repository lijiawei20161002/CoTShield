"""
Monitor an existing finetuning job
"""

import sys
import time
import json
from pathlib import Path
from openai import OpenAI

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)

def monitor_job(job_id, check_interval=60):
    """Monitor finetuning job until completion"""

    print(f"Monitoring finetuning job: {job_id}")
    print("="*70)

    while True:
        try:
            job = client.fine_tuning.jobs.retrieve(job_id)
            status = job.status

            print(f"\nStatus: {status}")

            if hasattr(job, 'created_at'):
                print(f"Created: {time.ctime(job.created_at)}")

            if hasattr(job, 'finished_at') and job.finished_at:
                print(f"Finished: {time.ctime(job.finished_at)}")

            if hasattr(job, 'trained_tokens') and job.trained_tokens:
                print(f"Trained tokens: {job.trained_tokens:,}")

            if status == "succeeded":
                print("\n" + "="*70)
                print("FINETUNING COMPLETED SUCCESSFULLY!")
                print("="*70)
                print(f"\nFine-tuned model: {job.fine_tuned_model}")

                # Save result
                result = {
                    'job_id': job_id,
                    'status': 'succeeded',
                    'finetuned_model': job.fine_tuned_model,
                    'finished_at': time.ctime(job.finished_at) if job.finished_at else None
                }

                result_file = DATA_DIR / "finetune_result.json"
                with open(result_file, 'w') as f:
                    json.dump(result, f, indent=2)

                print(f"\nResult saved to {result_file}")
                print("\nYou can now evaluate with:")
                print(f"  python scripts/7_evaluate.py --model {job.fine_tuned_model} --eval-type original")

                return job.fine_tuned_model

            elif status in ["failed", "cancelled"]:
                print("\n" + "="*70)
                print(f"FINETUNING {status.upper()}")
                print("="*70)

                if hasattr(job, 'error') and job.error:
                    print(f"\nError: {job.error}")

                return None

            elif status in ["validating_files", "queued", "running"]:
                # Show recent events
                try:
                    events = client.fine_tuning.jobs.list_events(job_id, limit=10)
                    if events.data:
                        print("\nRecent events:")
                        for event in events.data[:5]:
                            timestamp = time.ctime(event.created_at) if hasattr(event, 'created_at') else ''
                            print(f"  [{timestamp}] {event.message}")
                except Exception as e:
                    print(f"Could not fetch events: {e}")

                print(f"\nChecking again in {check_interval} seconds...")
                print("Press Ctrl+C to stop monitoring (job will continue)")

                time.sleep(check_interval)

            else:
                print(f"\nUnknown status: {status}")
                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped. Job is still running.")
            print(f"Resume monitoring with: python scripts/monitor_finetuning.py {job_id}")
            sys.exit(0)

        except Exception as e:
            print(f"\nError: {e}")
            print("Retrying in 60 seconds...")
            time.sleep(60)

def list_recent_jobs():
    """List recent finetuning jobs"""
    try:
        jobs = client.fine_tuning.jobs.list(limit=10)

        print("\nRecent finetuning jobs:")
        print("="*70)

        for job in jobs.data:
            print(f"\nJob ID: {job.id}")
            print(f"Status: {job.status}")
            print(f"Model: {job.model}")
            if job.fine_tuned_model:
                print(f"Fine-tuned model: {job.fine_tuned_model}")
            if hasattr(job, 'created_at'):
                print(f"Created: {time.ctime(job.created_at)}")

    except Exception as e:
        print(f"Error listing jobs: {e}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Monitor finetuning job')
    parser.add_argument('job_id', nargs='?', help='Finetuning job ID to monitor')
    parser.add_argument('--list', action='store_true', help='List recent jobs')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')

    args = parser.parse_args()

    if args.list:
        list_recent_jobs()
        return

    if not args.job_id:
        # Try to load from saved job info
        job_info_file = DATA_DIR / "finetune_job_info.json"
        if job_info_file.exists():
            with open(job_info_file, 'r') as f:
                job_info = json.load(f)
                args.job_id = job_info.get('job_id')

        if not args.job_id:
            print("Error: No job ID provided and no saved job info found")
            print("\nUsage:")
            print("  python scripts/monitor_finetuning.py <job_id>")
            print("  python scripts/monitor_finetuning.py --list")
            sys.exit(1)

    monitor_job(args.job_id, args.interval)

if __name__ == "__main__":
    main()
