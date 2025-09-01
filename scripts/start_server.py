#!/usr/bin/env python3
"""
OFS Mockup Server Startup Script

Simple startup script for the OFS Mockup Server with configurable parameters.
"""

import argparse
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


def kill_process_on_port(port):
    """Kill process using the specified port."""
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


def main():
    """Main entry point for starting the OFS Mockup Server."""
    parser = argparse.ArgumentParser(
        description="Start OFS Mockup Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_server.py                    # Start with defaults (port 8200, available)
  python start_server.py --port 3566       # Start on port 3566
  python start_server.py --unavailable     # Start with service unavailable
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8200, 
        help="Port to bind the server (default: 8200)"
    )
    
    parser.add_argument(
        "--unavailable",
        action="store_true",
        help="Start with service unavailable (default: available)"
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

    args = parser.parse_args()

    # Check if port is busy and kill if necessary
    if check_port(args.port):
        print(f"⚠️  Port {args.port} is busy")
        if not kill_process_on_port(args.port):
            print(f"❌ Cannot start server on port {args.port}")
            sys.exit(1)
    
    # Initialize app state from CLI args
    app.state.pin_fail_count = 0
    app.state.current_api_attention = 404 if args.unavailable else 200

    print(f"🚀 Starting OFS Mockup Server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Status: {'Unavailable' if args.unavailable else 'Available'}")
    print(f"   URL: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    print(f"   Service: {'404 on /api/attention' if args.unavailable else '200 on /api/attention'}")
    print()

    try:
        uvicorn.run(
            "ofs_mockup_srv.main:app",
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
            access_log=False,
            workers=1,
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()