"""
EMERGENCY FIX - Run this to fix version conflicts
"""
import subprocess
import sys
import os

print("="*70)
print("EMERGENCY FIX SCRIPT - Fixing Version Conflicts")
print("="*70)
print()

def run_command(cmd, description):
    """Run a command and show output"""
    print(f"⚙️  {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

print("Step 1: Uninstalling conflicting packages...")
print()

packages_to_remove = [
    "langchain",
    "langchain-community", 
    "langchain-core",
    "langchain-huggingface"
]

for package in packages_to_remove:
    run_command(f"pip uninstall {package} -y", f"Removing {package}")

print()
print("Step 2: Installing compatible versions...")
print()

# Install in correct order
commands = [
    ("pip install langchain-core==0.3.15", "Installing langchain-core"),
    ("pip install langchain-community==0.3.7", "Installing langchain-community"),
    ("pip install langchain==0.3.7", "Installing langchain"),
    ("pip install langchain-huggingface==0.1.0", "Installing langchain-huggingface"),
]

success = True
for cmd, desc in commands:
    if not run_command(cmd, desc):
        success = False
        break

print()
if success:
    print("="*70)
    print("✅ FIXED!")
    print("="*70)
    print()
    print("Now do this:")
    print()
    print("1. Replace src/llm_config.py with llm_config_ALTERNATIVE.py")
    print("   (This uses a simpler approach that avoids version conflicts)")
    print()
    print("2. Clear cache:")
    print("   del /s /q __pycache__")
    print()
    print("3. Test:")
    print("   python test_local.py")
    print()
else:
    print("="*70)
    print("⚠️  Some packages failed to install")
    print("="*70)
    print()
    print("Try manual installation:")
    print()
    print("pip install langchain-core==0.3.15")
    print("pip install langchain-community==0.3.7")
    print("pip install langchain==0.3.7")
    print("pip install langchain-huggingface==0.1.0")
    print()