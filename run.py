import sys
import os
import subprocess
import importlib.util

def check_dependencies():
    """Check for system dependencies"""
    # Check for tkinter
    if importlib.util.find_spec("tkinter") is None:
        print("\033[91mError: tkinter is not installed.\033[0m")
        print("Please install it using your package manager.")
        print("For Fedora: \033[93msudo dnf install python3-tkinter\033[0m")
        print("For Ubuntu/Debian: \033[93msudo apt-get install python3-tk\033[0m")
        return False
    return True

def check_x11_auth():
    """Check and try to fix X11 authorization"""
    try:
        # Try to run xhost to check access
        result = subprocess.run(['xhost'], capture_output=True, text=True)
        if result.returncode != 0:
            # Try to fix it for local user
            user = os.environ.get('USER', 'currrent_user')
            print(f"Attempting to fix X11 authorization for {user}...")
            subprocess.run(['xhost', f'+SI:localuser:{user}'], check=True)
            print("\033[92mX11 authorization fixed.\033[0m")
    except Exception as e:
        print(f"Warning: Could not check/fix X11 authorization: {e}")

# Add src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    check_x11_auth()
    
    try:
        from main import main
        main()
    except ImportError as e:
        if "DisplayConnectionError" in str(e) or "Authorization required" in str(e):
             print("\033[91mError: X11 Display Authorization Failed.\033[0m")
             print("Try running: \033[93mxhost +SI:localuser:$(whoami)\033[0m")
        else:
            raise e
