#!/usr/bin/env python
import subprocess
import sys
import time
import os
import threading
import queue
import urllib.request
import urllib.error


def ping_service(port, service_name, timeout=5):
    """Check if service is running"""
    url = f'http://localhost:{port}/health' if service_name == 'Analysis' else f'http://localhost:{port}/api/evaluation/health'
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(url, timeout=2)
            if response.status == 200:
                return True
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            time.sleep(0.5)

    return False


def read_output(process, service_name, output_queue):
    """Read process stdout and stderr"""
    try:
        while True:
            line = process.stdout.readline()
            if line:
                output_queue.put((service_name, line.rstrip()))
            else:
                break
    except Exception as e:
        output_queue.put((service_name, f"[ERROR] {str(e)}"))


def print_output(output_queue):
    """Print content from output queue"""
    try:
        while True:
            service_name, line = output_queue.get(timeout=0.1)
            if line:
                print(f"[{service_name}] {line}")
    except queue.Empty:
        pass


def run_services():
    """Run both Flask services simultaneously"""
    processes = []
    threads = []
    output_queue = queue.Queue()
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        print("\n" + "=" * 70)
        print(" " * 15 + "Starting Unified Backend Services")
        print("=" * 70)
        print()

        # Check if necessary files exist
        run_py = os.path.join(backend_dir, 'run.py')
        run_eval_py = os.path.join(backend_dir, 'run_evaluation.py')

        if not os.path.exists(run_py):
            print(f"Error: Cannot find {run_py}")
            sys.exit(1)

        if not os.path.exists(run_eval_py):
            print(f"Error: Cannot find {run_eval_py}")
            sys.exit(1)

        # Start Analysis service (run.py) - port 5000
        print("[1/2] Starting Analysis service (run.py - port 5000)...")
        try:
            analysis_process = subprocess.Popen(
                [sys.executable, 'run.py'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8'
            )
            processes.append(('Analysis', analysis_process))

            # Create log reading thread for Analysis service
            thread = threading.Thread(
                target=read_output,
                args=(analysis_process, 'Analysis', output_queue),
                daemon=True
            )
            threads.append(thread)
            thread.start()

            print("       ✓ Analysis service process started")
        except Exception as e:
            print(f"       ✗ Failed to start Analysis service: {e}")
            sys.exit(1)

        # Wait for Analysis service to start and verify
        print("       Waiting for Analysis service to start...")
        if ping_service(5000, 'Analysis', timeout=10):
            print("       ✓ Analysis service is ready")
        else:
            print(
                "       ⚠ Analysis service startup is slow, starting Evaluation service...")

        time.sleep(1)

        # Start Evaluation service (run_evaluation.py) - port 5001
        print("[2/2] Starting Evaluation service (run_evaluation.py - port 5001)...")
        try:
            evaluation_process = subprocess.Popen(
                [sys.executable, 'run_evaluation.py'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8'
            )
            processes.append(('Evaluation', evaluation_process))

            # Create log reading thread for Evaluation service
            thread = threading.Thread(
                target=read_output,
                args=(evaluation_process, 'Evaluation', output_queue),
                daemon=True
            )
            threads.append(thread)
            thread.start()

            print("       ✓ Evaluation service process started")
        except Exception as e:
            print(f"       ✗ Failed to start Evaluation service: {e}")
            sys.exit(1)

        # Wait for Evaluation service to start and verify
        print("       Waiting for Evaluation service to start...")
        if ping_service(5001, 'Evaluation', timeout=10):
            print("       ✓ Evaluation service is ready")
        else:
            print("       ⚠ Evaluation service startup is slow...")

        time.sleep(1)

        print()
        print("=" * 70)
        print("✓ All backend services started!")
        print("=" * 70)
        print()
        print("Service addresses:")
        print("  - Analysis service: http://localhost:5000")
        print("  - Evaluation service: http://localhost:5001")
        print()
        print("Service logs:")
        print("=" * 70)
        print()

        # Main loop: print output and monitor processes
        while True:
            # Print output
            print_output(output_queue)

            # Check if all processes are still running
            all_running = all(p.poll() is None for _, p in processes)
            if not all_running:
                print("\n[WARNING] A service has stopped")
                for service_name, process in processes:
                    if process.poll() is not None:
                        print(
                            f"  {service_name} service stopped (exit code: {process.returncode})")
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("Closing all backend services...")
        print("=" * 70)
        print()

        # Terminate all processes
        for service_name, process in processes:
            if process.poll() is None:
                print(f"Closing {service_name} service...")
                try:
                    process.terminate()
                    process.wait(timeout=3)
                    print(f"  ✓ {service_name} service closed")
                except subprocess.TimeoutExpired:
                    print(f"  Force closing {service_name} service...")
                    process.kill()
                    print(f"  ✓ {service_name} service force closed")

        print()
        print("=" * 70)
        print("All services closed")
        print("=" * 70)
        sys.exit(0)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

        # Clean up processes
        for service_name, process in processes:
            if process.poll() is None:
                print(f"Force closing {service_name}...")
                process.kill()
        sys.exit(1)


if __name__ == '__main__':
    run_services()
