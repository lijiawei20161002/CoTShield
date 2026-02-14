"""
Step 6: Run finetuning via OpenAI API
"""

import json
import sys
import time
from pathlib import Path
from openai import OpenAI

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)

def upload_file(file_path):
    """Upload file to OpenAI"""
    print(f"Uploading {file_path}...")

    with open(file_path, 'rb') as f:
        response = client.files.create(
            file=f,
            purpose='fine-tune'
        )

    print(f"File uploaded: {response.id}")
    return response.id

def create_finetune_job(train_file_id, val_file_id=None, model="gpt-4o-mini-2024-07-18", suffix=None):
    """Create a finetuning job"""

    print(f"\nCreating finetuning job for model: {model}")

    job_params = {
        "training_file": train_file_id,
        "model": model,
    }

    if val_file_id:
        job_params["validation_file"] = val_file_id

    if suffix:
        job_params["suffix"] = suffix

    # Hyperparameters
    job_params["hyperparameters"] = {
        "n_epochs": FINETUNE_EPOCHS
    }

    response = client.fine_tuning.jobs.create(**job_params)

    print(f"Finetuning job created: {response.id}")
    print(f"Status: {response.status}")

    return response.id

def monitor_finetune_job(job_id, check_interval=60):
    """Monitor finetuning job until completion"""

    print(f"\nMonitoring job {job_id}...")
    print("This may take 20-60 minutes depending on dataset size.")

    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status

        print(f"Status: {status}")

        if status == "succeeded":
            print(f"\nFinetuning completed!")
            print(f"Fine-tuned model: {job.fine_tuned_model}")
            return job.fine_tuned_model

        elif status in ["failed", "cancelled"]:
            print(f"\nFinetuning {status}")
            if hasattr(job, 'error'):
                print(f"Error: {job.error}")
            return None

        elif status in ["validating_files", "queued", "running"]:
            # Check for events
            try:
                events = client.fine_tuning.jobs.list_events(job_id, limit=5)
                if events.data:
                    print("Recent events:")
                    for event in events.data[:3]:
                        print(f"  - {event.message}")
            except:
                pass

            time.sleep(check_interval)

        else:
            print(f"Unknown status: {status}")
            time.sleep(check_interval)

def main():
    train_file = DATA_DIR / "finetuning_train.jsonl"
    val_file = DATA_DIR / "finetuning_val.jsonl"

    if not train_file.exists():
        print(f"Error: Training file not found at {train_file}")
        print("Please run 5_prepare_finetuning.py first")
        sys.exit(1)

    # Upload files
    train_file_id = upload_file(train_file)
    val_file_id = None
    if val_file.exists():
        val_file_id = upload_file(val_file)

    # Create finetuning job
    job_id = create_finetune_job(
        train_file_id,
        val_file_id,
        model=FINETUNE_BASE_MODEL,
        suffix="moral-reflective"
    )

    # Save job info
    job_info = {
        "job_id": job_id,
        "train_file_id": train_file_id,
        "val_file_id": val_file_id,
        "base_model": FINETUNE_BASE_MODEL,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    job_info_file = DATA_DIR / "finetune_job_info.json"
    with open(job_info_file, 'w') as f:
        json.dump(job_info, f, indent=2)

    print(f"\nJob info saved to {job_info_file}")
    print("\nYou can monitor the job with:")
    print(f"  python scripts/monitor_finetuning.py {job_id}")
    print("\nOr continue to monitor now...")

    response = input("Monitor job now? (y/n): ")
    if response.lower() == 'y':
        finetuned_model = monitor_finetune_job(job_id)

        if finetuned_model:
            job_info["finetuned_model"] = finetuned_model
            job_info["status"] = "succeeded"
            with open(job_info_file, 'w') as f:
                json.dump(job_info, f, indent=2)

            print(f"\nFine-tuned model: {finetuned_model}")
            print("You can now run evaluations with:")
            print(f"  python scripts/7_evaluate.py --model {finetuned_model}")

if __name__ == "__main__":
    main()
