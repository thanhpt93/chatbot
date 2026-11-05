import os
import subprocess
import time
import sys

def main():
    dump_path = os.path.abspath(r"database\inf_nffice_latest.dump")
    log_dir = os.path.abspath(r"artifacts\database-discovery")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(r"documentation\phase-1-database-discovery", exist_ok=True)
    
    log_file = os.path.join(log_dir, "restoration.log")
    
    pg_restore_exe = r"C:\Users\admin\miniconda3\envs\chat\Library\bin\pg_restore.exe"
    
    cmd = [
        pg_restore_exe,
        "-h", "127.0.0.1",
        "-p", "5433",
        "-U", "postgres",
        "-d", "inf_nffice",
        "--verbose",
        "--no-owner",
        "--no-privileges",
        dump_path
    ]
    
    print(f"Starting restoration of {dump_path} into inf_nffice on port 5433...")
    t0 = time.time()
    
    with open(log_file, "w", encoding="utf-8") as lf:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        entry_count = 0
        warning_count = 0
        error_count = 0
        
        for line in proc.stdout:
            lf.write(line)
            if "pg_restore: processing item" in line:
                entry_count += 1
                if entry_count % 200 == 0:
                    print(f"Processed {entry_count} items...")
            elif "warning" in line.lower():
                warning_count += 1
            elif "error" in line.lower():
                error_count += 1
                
        proc.wait()
        
    duration = time.time() - t0
    exit_code = proc.returncode
    print(f"Restoration finished in {duration:.2f} seconds.")
    print(f"Exit code: {exit_code}")
    print(f"Processed items: {entry_count}")
    print(f"Warnings: {warning_count}, Errors: {error_count}")
    print(f"Log written to: {log_file}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
