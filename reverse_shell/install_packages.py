import subprocess

def install_package(package_name):
    try:
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', package_name])
        print(f"{package_name} installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package_name}: {e}")

# Instalare python3-pip
install_package('python3-pip')

# Încercare de instalare a pachetului mss
try:
    import mss
except ImportError:
    # În cazul în care modulul mss nu este disponibil, îl instalăm
    install_package('python3-mss')
    # După instalare, încercăm din nou importul
    try:
        import mss
    except ImportError:
        print("Failed to install mss. Please check your internet connection and try again.")
