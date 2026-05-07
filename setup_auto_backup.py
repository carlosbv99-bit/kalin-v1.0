"""
Setup Windows Task Scheduler for automatic GitHub backups
Run this once to configure automatic backups
"""
import subprocess
import sys
import os

def setup_scheduled_task():
    """Create a Windows scheduled task for auto-backup"""
    
    print("="*60)
    print("  SETUP AUTO-BACKUP SCHEDULE")
    print("="*60)
    print()
    
    # Get current directory
    project_dir = os.getcwd()
    script_path = os.path.join(project_dir, "auto_backup.bat")
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    print("Configuration options:")
    print()
    print("1. Backup frequency:")
    print("   a) Every hour")
    print("   b) Every 4 hours")
    print("   c) Twice daily (9 AM, 6 PM)")
    print("   d) Daily at 6 PM")
    print()
    
    choice = input("Select option (a/b/c/d) [default: c]: ").strip().lower()
    
    # Set schedule based on choice
    if choice == 'a':
        schedule = "HOURLY"
        interval = "1"
        description = "Every hour"
    elif choice == 'b':
        schedule = "HOURLY"
        interval = "4"
        description = "Every 4 hours"
    elif choice == 'd':
        schedule = "DAILY"
        time = "18:00"
        description = "Daily at 6 PM"
    else:  # Default: c
        schedule = "TWICE_DAILY"
        description = "Twice daily (9 AM, 6 PM)"
    
    print()
    print(f"Selected: {description}")
    print()
    
    # Confirm
    confirm = input("Create scheduled task? (y/n) [default: y]: ").strip().lower()
    if confirm == 'n':
        print("Cancelled")
        return False
    
    print()
    print("Creating scheduled task...")
    
    try:
        if schedule == "HOURLY":
            # Hourly backup
            cmd = f'schtasks /create /tn "Kalin Auto-Backup" /tr "{script_path}" /sc hourly /mo {interval} /ru SYSTEM'
        elif schedule == "DAILY":
            # Daily at specific time
            cmd = f'schtasks /create /tn "Kalin Auto-Backup" /tr "{script_path}" /sc daily /st {time} /ru SYSTEM'
        elif schedule == "TWICE_DAILY":
            # Create two tasks
            cmd1 = f'schtasks /create /tn "Kalin Auto-Backup Morning" /tr "{script_path}" /sc daily /st 09:00 /ru SYSTEM'
            cmd2 = f'schtasks /create /tn "Kalin Auto-Backup Evening" /tr "{script_path}" /sc daily /st 18:00 /ru SYSTEM'
            
            result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
            result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
            
            if result1.returncode == 0 and result2.returncode == 0:
                print("✅ Scheduled tasks created successfully!")
                print()
                print("Tasks:")
                print("  - Kalin Auto-Backup Morning (9:00 AM)")
                print("  - Kalin Auto-Backup Evening (6:00 PM)")
                return True
            else:
                print("❌ Failed to create scheduled tasks")
                if result1.stderr:
                    print(f"Error 1: {result1.stderr}")
                if result2.stderr:
                    print(f"Error 2: {result2.stderr}")
                return False
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Scheduled task created successfully!")
            print()
            print(f"Task Name: Kalin Auto-Backup")
            print(f"Schedule: {description}")
            print(f"Script: {script_path}")
            print()
            print("To view task:")
            print("  schtasks /query /tn \"Kalin Auto-Backup\"")
            print()
            print("To delete task:")
            print("  schtasks /delete /tn \"Kalin Auto-Backup\" /f")
            return True
        else:
            print("❌ Failed to create scheduled task")
            print(f"Error: {result.stderr}")
            print()
            print("Try running as Administrator")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def show_existing_tasks():
    """Show existing scheduled tasks"""
    print("Checking for existing Kalin backup tasks...")
    print()
    
    result = subprocess.run('schtasks /query /fo list | findstr "Kalin"', 
                          shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("Found tasks:")
        print(result.stdout)
    else:
        print("No existing Kalin backup tasks found")

def main():
    """Main function"""
    print()
    print("This will set up automatic GitHub backups using Windows Task Scheduler")
    print("You need Administrator privileges to create scheduled tasks")
    print()
    
    # Show existing tasks
    show_existing_tasks()
    print()
    
    # Ask to setup
    setup = input("Setup automatic backup schedule? (y/n) [default: y]: ").strip().lower()
    
    if setup != 'n':
        success = setup_scheduled_task()
        
        if success:
            print()
            print("="*60)
            print("  SETUP COMPLETE")
            print("="*60)
            print()
            print("Your code will now automatically backup to GitHub!")
            print()
            print("Manual backup command:")
            print("  python auto_backup_github.py")
            print()
    else:
        print("Setup cancelled")

if __name__ == "__main__":
    main()
