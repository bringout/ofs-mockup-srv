#!/usr/bin/env python3
"""
OFS Mockup Server Startup Script

Simple startup script for the OFS Mockup Server with configurable parameters.
"""

import argparse
import uvicorn
from ofs_mockup_srv.main import app, DEFAULT_GSC


def main():
    """Main entry point for starting the OFS Mockup Server."""
    parser = argparse.ArgumentParser(
        description="Start OFS Mockup Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_server.py                    # Start with defaults (port 8200, GSC 9999)
  python start_server.py --port 3566       # Start on port 3566
  python start_server.py --gsc 1500        # Start with PIN required
  python start_server.py --gsc 1300        # Start with security element missing
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8200, 
        help="Port to bind the server (default: 8200)"
    )
    
    parser.add_argument(
        "--gsc", 
        default=DEFAULT_GSC, 
        choices=["1300", "1500", "9999"],
        help="Initial GSC (General Status Code): 1300=no security element, 1500=PIN required, 9999=ready (default: 9999)"
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

    # Initialize app state from CLI args
    app.state.gsc = str(args.gsc)
    app.state.pin_fail_count = 0

    print(f"🚀 Starting OFS Mockup Server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   GSC: {args.gsc} ({'Ready' if args.gsc == '9999' else 'PIN Required' if args.gsc == '1500' else 'No Security Element'})")
    print(f"   URL: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    print()

    uvicorn.run(
        "ofs_mockup_srv.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        access_log=False,
        workers=1,
    )


if __name__ == "__main__":
    main()