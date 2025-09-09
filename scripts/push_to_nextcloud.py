#!/usr/bin/env python3
"""
NextCloud Upload Script for OFS Mockup Server
Builds a wheel and uploads it to NextCloud.
"""

import os
import sys
import subprocess
import argparse
import platform
import zipfile
from pathlib import Path


def get_environment_vars():
    """Get required environment variables for NextCloud authentication"""
    nc_user = os.getenv('NC_USER')
    nc_api_key = os.getenv('NC_API_KEY')
    
    if not nc_user:
        print("Error: NC_USER environment variable not set", file=sys.stderr)
        return None, None
    
    if not nc_api_key:
        print("Error: NC_API_KEY environment variable not set", file=sys.stderr)
        print("Set it with: export NC_API_KEY=`pass hernad/next.cloud.out.ba/api_key`", file=sys.stderr)
        return None, None
    
    return nc_user, nc_api_key


def get_platform_info():
    """Deprecated: kept for compatibility; no longer used."""
    return 'any', 'whl'


def upload_to_nextcloud(file_path, nc_user, nc_api_key, remote_filename):
    """Upload file to NextCloud using curl with WebDAV"""
    # Use WebDAV endpoint for uploads to user's packages folder
    remote_auth = f"{nc_user}@bring.out.ba:{nc_api_key}"
    remote_url = f"https://next.cloud.out.ba/remote.php/dav/files/{nc_user}@bring.out.ba/packages/{remote_filename}"
    
    curl_cmd = [
        'curl',
        '-u', remote_auth,
        '-T', str(file_path),
        remote_url
    ]
    
    print(f"Uploading {file_path} to {remote_url}")
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Upload successful!")
            return True
        else:
            print(f"Upload failed with return code {result.returncode}", file=sys.stderr)
            print(f"Error output: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error running curl: {e}", file=sys.stderr)
        return False


def download_from_nextcloud(nc_user, nc_api_key, remote_filename, local_path):
    """Download file from NextCloud using curl with WebDAV"""
    # Use WebDAV endpoint for downloads from user's packages folder
    remote_auth = f"{nc_user}@bring.out.ba:{nc_api_key}"
    remote_url = f"https://next.cloud.out.ba/remote.php/dav/files/{nc_user}@bring.out.ba/packages/{remote_filename}"
    
    curl_cmd = [
        'curl',
        '-u', remote_auth,
        '-o', str(local_path),
        remote_url
    ]
    
    print(f"Downloading {remote_url} to {local_path}")
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Download successful! File saved as: {local_path}")
            return True
        else:
            print(f"Download failed with return code {result.returncode}", file=sys.stderr)
            print(f"Error output: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error running curl: {e}", file=sys.stderr)
        return False


def print_help():
    """Print comprehensive help message"""
    help_text = r"""
OFS Mockup Server NextCloud Upload Script
========================================

DESCRIPTION:
    This script builds and uploads OFS Mockup Server packages to NextCloud for distribution.
    By default, it builds and uploads a wheel package (.whl file).

USAGE:
    python scripts/push_to_nextcloud.py [OPTIONS]

OPTIONS:
    -h, --help          Show this help message and exit
    --dry-run          Build package but don't upload (testing)
    --verbose          Enable verbose output
    --download         After upload, download file to current directory
    --wheel            Build and upload wheel package (DEFAULT - can be omitted)
    --wheelhouse       Build and upload Windows wheelhouse zip for offline install
                       (replaces wheel with: ofs_mockup_srv_wheelhouse_windows_{date}_pyXY_arch.zip)

ENVIRONMENT VARIABLES:
    NC_USER            NextCloud username (required)
                       Example: export NC_USER=hernad
    
    NC_API_KEY         NextCloud API key (required)
                       Example: export NC_API_KEY=`pass hernad/next.cloud.out.ba/api_key`

UPLOAD DESTINATION:
    https://next.cloud.out.ba/remote.php/dav/files/{NC_USER}/packages/

PREREQUISITES:
    1. Environment Setup:
       export NC_USER=hernad
       export NC_API_KEY=`pass hernad/next.cloud.out.ba/api_key`
    
    2. Dependencies:
       - curl (for upload)
       - uv (for building wheel)
    
    3. Authentication:
       - NextCloud account with API access
       - API key stored in password manager

EXAMPLES:
    # Build and upload wheel to NextCloud (default behavior)
    python scripts/push_to_nextcloud.py
    
    # Explicitly specify wheel (same as default)
    python scripts/push_to_nextcloud.py --wheel
    
    # Test wheel build without uploading
    python scripts/push_to_nextcloud.py --dry-run
    
    # Verbose output for debugging
    python scripts/push_to_nextcloud.py --verbose
    
    # Upload wheel and download back to current directory
    python scripts/push_to_nextcloud.py --download

    # Build and upload Windows wheelhouse (instead of wheel)
    python scripts/push_to_nextcloud.py --wheelhouse

WORKFLOW:
    DEFAULT (wheel):
    1. Validate environment variables (NC_USER, NC_API_KEY)
    2. Build wheel using uv build -> ofs_mockup_srv-{version}-py3-none-any.whl
    3. Upload wheel to NextCloud using curl
    4. Optionally download file back to current directory (--download)
    
    WHEELHOUSE mode (--wheelhouse):
    1. Validate environment variables
    2. Build wheel + download all dependencies
    3. Create wheelhouse zip -> ofs_mockup_srv_wheelhouse_windows_{date}_py{ver}_{arch}.zip
    4. Upload wheelhouse to NextCloud using curl
    5. Optionally download file back to current directory (--download)

ERROR CODES:
    0   Success
    1   Environment variable missing
    2   Build failed
    3   Reserved
    4   Upload failed
    5   Invalid arguments

TROUBLESHOOTING:
    - Environment Variables:
      Check: echo $NC_USER $NC_API_KEY
      
    - Network Issues:
      Test with: curl -u $NC_USER@bring.out.ba:$NC_API_KEY https://next.cloud.out.ba
      
    - Permissions:
      Ensure script is executable: chmod +x scripts/push_to_nextcloud.py

AUTHOR:
    Ernad Husremovic <hernad@bring.out.ba>
    bring.out doo Sarajevo
    https://www.bring.out.ba
"""
    print(help_text)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Build and upload OFS Mockup Server wheel to NextCloud",
        add_help=False  # We'll handle help ourselves
    )
    
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show comprehensive help message')
    parser.add_argument('--dry-run', action='store_true',
                       help='Build wheel but don\'t upload')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--download', action='store_true',
                       help='After upload, download file back to current directory')
    parser.add_argument('--wheel', action='store_true', default=True,
                       help='Build and upload wheel package (default)')
    parser.add_argument('--wheelhouse', action='store_true',
                       help='Build Windows offline wheelhouse zip and upload (instead of wheel)')
    
    return parser.parse_args()


def build_wheel_package():
    """Build wheel package using uv build"""
    print("Building wheel package...")
    
    try:
        result = subprocess.run(['uv', 'build'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Wheel package built successfully")
            
            # Find the latest .whl file in dist/
            project_root = Path(__file__).parent.parent
            dist_dir = project_root / 'dist'
            
            if not dist_dir.exists():
                print("Error: dist/ directory not found after build", file=sys.stderr)
                return None
                
            whl_files = list(dist_dir.glob('*.whl'))
            if not whl_files:
                print("Error: No .whl files found in dist/", file=sys.stderr)
                return None
                
            # Return the most recently created wheel file
            latest_whl = max(whl_files, key=lambda p: p.stat().st_mtime)
            print(f"Built wheel: {latest_whl}")
            return latest_whl
            
        else:
            print(f"Error building wheel: {result.stderr}", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"Error running 'uv build': {e}", file=sys.stderr)
        return None

def _normalize_arch(name: str) -> str:
    n = name.lower()
    if n in ("x86_64", "amd64"):
        return "amd64"
    if n in ("aarch64", "arm64"):
        return "arm64"
    return n


def _get_project_version() -> str:
    """Read version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
    try:
        txt = pyproject_path.read_text(encoding='utf-8')
    except Exception:
        return "unknown"
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith('version') and '=' in line:
            try:
                return line.split('=')[1].strip().strip('"')
            except Exception:
                pass
    return "unknown"




def _get_project_dependencies() -> list[str]:
    """Parse [project] dependencies from pyproject.toml (rough, but works)."""
    pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
    try:
        txt = pyproject_path.read_text(encoding='utf-8')
    except Exception:
        return []
    deps: list[str] = []
    in_proj = False
    in_deps = False
    for line in txt.splitlines():
        t = line.strip()
        if t.startswith('[project]'):
            in_proj = True
            continue
        if in_proj and t.startswith('[') and not t.startswith('[project]'):
            break
        if in_proj:
            if t.startswith('dependencies') and t.endswith('[') or t.startswith('dependencies = ['):
                in_deps = True
                # collect after first [ if on same line
                after = t.split('[',1)[1]
                if after.strip().endswith(']'):
                    inner = after.rsplit(']',1)[0]
                    parts = [x.strip().strip('"') for x in inner.split(',') if x.strip()]
                    deps.extend([p for p in parts if p])
                    in_deps = False
                continue
            if in_deps:
                if t.startswith(']'):
                    in_deps = False
                    continue
                # lines like "requests>=2.25.0",
                if t.endswith(','):
                    t = t[:-1]
                t = t.strip().strip('"')
                if t:
                    deps.append(t)
    return deps


def _get_uv_lock_tag(project_root: Path) -> str | None:
    """Return uv.lock modified date as YYYYMMDD, or None if missing."""
    lock_path = project_root / 'uv.lock'
    if not lock_path.exists():
        return None
    try:
        import datetime as _dt
        ts = lock_path.stat().st_mtime
        dt = _dt.datetime.utcfromtimestamp(ts)
        return dt.strftime('%Y%m%d')
    except Exception:
        return None

def build_windows_wheelhouse_zip(verbose: bool = False):
    """Build a Windows wheelhouse zip for offline installation and return its path.

    The archive contains:
      - wheelhouse/ (all dependency wheels + the built ofs-mockup-srv wheel)
      - requirements.txt (pinned from uv.lock, plus 'ofs-mockup-srv==<version>')
    """
    project_root = Path(__file__).parent.parent

    # Build local wheel first
    wheel_path = build_wheel_package()
    if not wheel_path:
        return None

    version = _get_project_version()
    pyver = f"{sys.version_info.major}{sys.version_info.minor}"
    arch = _normalize_arch(platform.machine())
    lock_tag = _get_uv_lock_tag(project_root)
    base_tag = (lock_tag or f"v{version}")
    version_tag = f"{base_tag}_py{pyver}_{arch}"
    zip_name = f"ofs_mockup_srv_wheelhouse_windows_{version_tag}.zip"

    # Prepare temp workspace
    import tempfile
    tmpdir = Path(tempfile.mkdtemp(prefix='ofs_mockup_srv_wheelhouse_'))
    wheelhouse_dir = tmpdir / 'wheelhouse'
    wheelhouse_dir.mkdir(parents=True, exist_ok=True)
    deps_req = tmpdir / 'requirements_deps.txt'
    final_req = tmpdir / 'requirements.txt' 

    if verbose:
        print(f"Temporary wheelhouse dir: {wheelhouse_dir}")
        print(f"Temporary requirements (deps): {deps_req}")

    # Create requirements files: deps-only and final with ofs-mockup-srv pin
    try:
        deps = _get_project_dependencies()
        with deps_req.open('w', encoding='utf-8') as f:
            for d in deps:
                f.write(d + '\n')
        with final_req.open('w', encoding='utf-8') as f:
            for d in deps:
                f.write(d + '\n')
            f.write(f"ofs-mockup-srv=={version}\n")
    except Exception as e:
        print(f"Error writing requirements files: {e}", file=sys.stderr)
        import shutil as _sh
        _sh.rmtree(tmpdir, ignore_errors=True)
        return None

    # Download all dependency wheels into wheelhouse
    try:
        dl = subprocess.run(
            ['uv', 'pip', 'download', '-r', str(deps_req), '-d', str(wheelhouse_dir)],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if dl.returncode != 0:
            # Fallback to pip if uv pip doesn't support download
            dl = subprocess.run(
                [sys.executable, '-m', 'pip', 'download', '-r', str(deps_req), '-d', str(wheelhouse_dir)],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            if dl.returncode != 0:
                print(f"Error downloading wheels (uv/pip): {dl.stderr}", file=sys.stderr)
                import shutil as _sh
                _sh.rmtree(tmpdir, ignore_errors=True)
                return None
    except Exception as e:
        print(f"Error running dependency download: {e}", file=sys.stderr)
        import shutil as _sh
        _sh.rmtree(tmpdir, ignore_errors=True)
        return None

    # Copy built ofs-mockup-srv wheel into wheelhouse
    try:
        import shutil as _sh
        _sh.copy2(wheel_path, wheelhouse_dir / wheel_path.name)
    except Exception as e:
        print(f"Error copying built wheel: {e}", file=sys.stderr)
        import shutil as _sh
        _sh.rmtree(tmpdir, ignore_errors=True)
        return None

    # Create zip containing wheelhouse/ and requirements.txt
    zip_path = tmpdir / zip_name
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # add requirements.txt at root
            zf.write(final_req, arcname='requirements.txt')
            # add wheelhouse content
            for root, _, files in os.walk(wheelhouse_dir):
                for file in files:
                    fpath = Path(root) / file
                    arcname = Path('wheelhouse') / fpath.relative_to(wheelhouse_dir)
                    zf.write(fpath, arcname=str(arcname))
        if verbose:
            print(f"Created wheelhouse zip: {zip_path}")
        return zip_path
    except Exception as e:
        print(f"Error creating wheelhouse zip: {e}", file=sys.stderr)
        import shutil as _sh
        _sh.rmtree(tmpdir, ignore_errors=True)
        return None



def main():
    """Main function to orchestrate the upload process"""
    args = parse_arguments()
    
    # Handle help
    if args.help:
        print_help()
        return 0
    
    if not args.dry_run:
        print("OFS Mockup Server NextCloud Upload Script")
        print("=" * 50)
    else:
        print("OFS Mockup Server NextCloud Upload Script (DRY RUN)")
        print("=" * 55)
    
    # Get environment variables
    nc_user, nc_api_key = get_environment_vars()
    if not nc_user or not nc_api_key:
        return 1
    
    # Determine what to build and upload
    if args.wheelhouse:
        # Wheelhouse mode: build offline Windows wheelhouse zip and upload
        if platform.system().lower() != 'windows':
            print("Warning: --wheelhouse is intended to be run on Windows to fetch Windows wheels.")
        zip_path = build_windows_wheelhouse_zip(verbose=args.verbose)
        if not zip_path:
            return 2

        if args.dry_run:
            print(f"DRY RUN: Would upload {zip_path.name} to NextCloud")
            return 0

        if not upload_to_nextcloud(zip_path, nc_user, nc_api_key, zip_path.name):
            return 4

        if args.download:
            current_dir = Path.cwd()
            local_download_path = current_dir / zip_path.name
            print(f"\nDownloading {zip_path.name} back to current directory...")
            if not download_from_nextcloud(nc_user, nc_api_key, zip_path.name, local_download_path):
                print("Warning: Upload successful but download failed", file=sys.stderr)
                return 0

        print(f"Successfully uploaded {zip_path.name} to NextCloud!")
        return 0

    # Default: Build wheel package only
    wheel_path = build_wheel_package()
    if not wheel_path:
        print("Error: Could not build wheel package", file=sys.stderr)
        return 2

    if args.verbose:
        print(f"Wheel file: {wheel_path}")
        print(f"NextCloud user: {nc_user}")
        print()

    if args.dry_run:
        print(f"DRY RUN: Would upload {wheel_path.name} to NextCloud")
        return 0

    # Upload wheel directly to NextCloud
    if not upload_to_nextcloud(wheel_path, nc_user, nc_api_key, wheel_path.name):
        return 4

    # Download back if requested
    if args.download:
        current_dir = Path.cwd()
        local_download_path = current_dir / wheel_path.name
        print(f"\nDownloading {wheel_path.name} back to current directory...")
        if not download_from_nextcloud(nc_user, nc_api_key, wheel_path.name, local_download_path):
            print("Warning: Upload successful but download failed", file=sys.stderr)
            return 0  # Still return success since upload worked

    print(f"Successfully uploaded {wheel_path.name} to NextCloud!")
    return 0


if __name__ == "__main__":
    sys.exit(main())