#!/usr/bin/env python3
"""
Kaggle Dataset Sync Script for Rosalia UK IT Market Analysis

This script syncs the ITJobsWatch market analysis data to Kaggle.
Credentials are loaded from .env file.

Setup:
1. Ensure .env file contains KAGGLE_USERNAME and KAGGLE_KEY
2. Run: python kaggle_sync.py
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
import subprocess
import sys
from dotenv import load_dotenv

class KaggleDatasetSync:
    def __init__(self, dataset_name="rosalia-uk-it-market"):
        self.dataset_name = dataset_name
        self.base_dir = Path.cwd()
        self.staging_dir = self.base_dir / "kaggle_staging"
        self.username = None
        
        # Load environment variables
        load_dotenv()
        
    def check_credentials(self):
        """Check if Kaggle credentials are configured"""
        # First check environment variables
        kaggle_username = os.getenv('KAGGLE_USERNAME')
        kaggle_key = os.getenv('KAGGLE_KEY')
        
        if kaggle_username and kaggle_key:
            self.username = kaggle_username
            # Set environment variables for Kaggle CLI
            os.environ['KAGGLE_USERNAME'] = kaggle_username
            os.environ['KAGGLE_KEY'] = kaggle_key
            print(f"[OK] Using Kaggle credentials from .env for user: {self.username}")
            return True
        
        # Fallback to kaggle.json file
        kaggle_json_paths = [
            Path.home() / ".kaggle" / "kaggle.json",
            Path(os.environ.get("USERPROFILE", "")) / ".kaggle" / "kaggle.json" if os.name == 'nt' else None
        ]
        
        for path in kaggle_json_paths:
            if path and path.exists():
                with open(path, 'r') as f:
                    creds = json.load(f)
                    self.username = creds.get('username')
                    print(f"[OK] Found Kaggle credentials in {path} for user: {self.username}")
                    return True
        
        print("[ERROR] Kaggle credentials not found!")
        print("\nTo set up Kaggle API credentials:")
        print("Option 1 - Use .env file (recommended):")
        print("  Add to .env file:")
        print("    KAGGLE_USERNAME=your_username")
        print("    KAGGLE_KEY=your_api_key")
        print("\nOption 2 - Use kaggle.json:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Click 'Create New API Token'")
        print("3. Save kaggle.json to ~/.kaggle/")
        return False
    
    def prepare_staging(self):
        """Prepare staging directory with data to upload"""
        print("\nPreparing staging directory...")
        
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
        self.staging_dir.mkdir(exist_ok=True)
        
        # Copy data directories
        data_mappings = {
            "api/data/manual": "manual_data",
            "api/data/scraped/itjobswatch": "itjobswatch_data",
            "reports": "analysis_reports",
            "docs/market-reports": "market_reports"
        }
        
        for source, dest in data_mappings.items():
            source_path = self.base_dir / source
            dest_path = self.staging_dir / dest
            
            if source_path.exists():
                print(f"  Copying {source} -> {dest}")
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, dest_path)
        
        # Copy important documentation
        for doc in ["README.md", "dataset-metadata.json"]:
            if (self.base_dir / doc).exists():
                shutil.copy2(self.base_dir / doc, self.staging_dir / doc)
                print(f"  Copied {doc}")
        
        print(f"[OK] Staging directory prepared at: {self.staging_dir}")
        
    def create_dataset(self):
        """Create or update the Kaggle dataset"""
        print("\nSyncing to Kaggle...")
        
        # Check if dataset exists
        check_cmd = f"kaggle datasets list -u {self.username} -s {self.dataset_name}"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        dataset_exists = self.dataset_name in result.stdout
        
        if not dataset_exists:
            print("Creating new dataset...")
            # Initialize new dataset
            os.chdir(self.staging_dir)
            init_cmd = f"kaggle datasets init -p ."
            subprocess.run(init_cmd, shell=True)
            
            # Update metadata
            with open("dataset-metadata.json", "r") as f:
                metadata = json.load(f)
            
            metadata["id"] = f"{self.username}/{self.dataset_name}"
            metadata["title"] = "UK IT Market Analysis - ITJobsWatch Data"
            
            with open("dataset-metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Create dataset
            create_cmd = "kaggle datasets create -p . -q"
            result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[OK] Dataset created successfully!")
                print(f"  View at: https://www.kaggle.com/datasets/{self.username}/{self.dataset_name}")
            else:
                print(f"[ERROR] Failed to create dataset: {result.stderr}")
                return False
        else:
            print("Updating existing dataset...")
            os.chdir(self.staging_dir)
            
            # Create version update
            update_cmd = f'kaggle datasets version -p . -m "Updated with latest market data"'
            result = subprocess.run(update_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[OK] Dataset updated successfully!")
                print(f"  View at: https://www.kaggle.com/datasets/{self.username}/{self.dataset_name}")
            else:
                print(f"[ERROR] Failed to update dataset: {result.stderr}")
                return False
        
        return True
    
    def cleanup(self):
        """Clean up staging directory"""
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
            print("[OK] Cleaned up staging directory")
    
    def run(self):
        """Run the complete sync process"""
        print("Starting Kaggle Dataset Sync")
        print("=" * 50)
        
        if not self.check_credentials():
            return False
        
        try:
            self.prepare_staging()
            success = self.create_dataset()
            
            if success:
                print("\n[SUCCESS] Sync completed successfully!")
            else:
                print("\n[FAILED] Sync failed. Please check the errors above.")
            
            return success
            
        except Exception as e:
            print(f"\n[ERROR] Error during sync: {e}")
            return False
        finally:
            os.chdir(self.base_dir)
            # Optionally cleanup
            # self.cleanup()

def main():
    # Check if custom dataset name provided
    dataset_name = sys.argv[1] if len(sys.argv) > 1 else "rosalia-uk-it-market"
    
    syncer = KaggleDatasetSync(dataset_name)
    success = syncer.run()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()