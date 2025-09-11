#!/usr/bin/env python3
"""
OFS Mockup Server Startup Script

Console script entry point for starting the OFS Mockup Server with configurable parameters.
Windows-compatible version of scripts/start_server.py
"""

import argparse
import os
import platform
import socket
import subprocess
import sys
import time
import uvicorn
from ofs_mockup_srv.main import app


def check_port(port):
    """Check if port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        return result == 0


def kill_process_on_port_windows(port):
    """Kill process using the specified port on Windows."""
    try:
        # Find process using the port using netstat
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True, text=True, check=False
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to run netstat")
            return False
            
        # Parse netstat output to find PIDs using the port
        pids_to_kill = []
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        if not pids_to_kill:
            print(f"⚠️  No process found using port {port}")
            return True
            
        # Kill found processes
        for pid in pids_to_kill:
            print(f"🔪 Killing process {pid} on port {port}...")
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], 
                             check=False, capture_output=True)
            except Exception as e:
                print(f"⚠️  Could not kill process {pid}: {e}")
        
        # Wait a bit for processes to terminate
        time.sleep(2)
        
        # Verify port is free
        if check_port(port):
            print(f"❌ Failed to free port {port}")
            return False
        else:
            print(f"✅ Port {port} is now free")
            return True
            
    except Exception as e:
        print(f"❌ Error killing process on port {port}: {e}")
        return False


def kill_process_on_port_unix(port):
    """Kill process using the specified port on Unix/Linux."""
    try:
        # Find process using the port
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True, text=True, check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🔪 Killing process {pid} on port {port}...")
                    subprocess.run(['kill', '-9', pid], check=False)
            
            # Wait a bit for processes to terminate
            time.sleep(1)
            
            # Verify port is free
            if check_port(port):
                print(f"❌ Failed to free port {port}")
                return False
            else:
                print(f"✅ Port {port} is now free")
                return True
        else:
            print(f"⚠️  No process found using port {port}")
            return True
            
    except FileNotFoundError:
        print("❌ lsof command not found. Cannot kill processes on port.")
        return False
    except Exception as e:
        print(f"❌ Error killing process on port {port}: {e}")
        return False


def kill_process_on_port(port):
    """Kill process using the specified port (cross-platform)."""
    if platform.system() == 'Windows':
        return kill_process_on_port_windows(port)
    else:
        return kill_process_on_port_unix(port)


def main():
    """Main entry point for starting the OFS Mockup Server."""
    parser = argparse.ArgumentParser(
        description="Start OFS Mockup Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  start-ofs-server                                # Start with defaults (port 8200, unavailable, PIN 4321)
  start-ofs-server --port 3566                   # Start on port 3566
  start-ofs-server --available                   # Start with service available
  start-ofs-server --pin 1234                    # Set custom PIN
  start-ofs-server --debug                       # Start with debug logging enabled
  start-ofs-server --debug --available --pin 0000 # Debug + available + custom PIN
  start-ofs-server --return-invoice-error "Out of paper:-10" # Simulate invoice errors
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8200, 
        help="Port to bind the server (default: 8200)"
    )
    
    parser.add_argument(
        "--available",
        action="store_true",
        help="Start with service available (default: unavailable)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload in development mode"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with request/response logging"
    )
    
    parser.add_argument(
        "--pin",
        default="4321",
        help="Set PIN for device authentication (default: 4321)"
    )
    
    parser.add_argument(
        "--return-invoice-error",
        help="Simulate invoice error in format 'message:errorCode' (e.g. 'Out of paper:-10')"
    )

    args = parser.parse_args()

    # Check if port is busy and kill if necessary
    if check_port(args.port):
        print(f"⚠️  Port {args.port} is busy")
        if not kill_process_on_port(args.port):
            print(f"❌ Cannot start server on port {args.port}")
            sys.exit(1)
    
    # Set environment variables for the server process
    os.environ['OFS_MOCKUP_DEBUG'] = 'true' if args.debug else 'false'
    os.environ['OFS_MOCKUP_PIN'] = args.pin
    os.environ['OFS_MOCKUP_AVAILABLE'] = 'true' if args.available else 'false'
    if args.return_invoice_error:
        os.environ['OFS_MOCKUP_INVOICE_ERROR'] = args.return_invoice_error
    
    # Initialize app state from CLI args
    app.state.pin_fail_count = 0
    app.state.current_api_attention = 200 if args.available else 404
    app.state.debug_enabled = args.debug
    app.state.pin = args.pin
    if args.return_invoice_error:
        app.state.invoice_error = args.return_invoice_error

    print(f"🚀 Starting OFS Mockup Server...", flush=True)
    print(f"   Host: {args.host}", flush=True)
    print(f"   Port: {args.port}", flush=True)
    print(f"   Status: {'Available' if args.available else 'Unavailable'}", flush=True)
    print(f"   URL: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}", flush=True)
    print(f"   Service: {'200 on /api/attention' if args.available else '404 on /api/attention'}", flush=True)
    print(f"   Platform: {platform.system()}", flush=True)
    if args.debug:
        print(f"   PIN: {args.pin}", flush=True)
    print(f"   Debug: {'Enabled - request/response logging' if args.debug else 'Disabled'}", flush=True)
    print(flush=True)

    try:
        uvicorn.run(
            "ofs_mockup_srv.main:app",
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
            access_log=args.debug,  # Enable access log when debug is on
            log_level="debug" if args.debug else "info",
            workers=1,
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()