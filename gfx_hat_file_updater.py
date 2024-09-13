import os
import shutil
import subprocess
import toml

def find_pwnagotchi_dir():
    possible_dirs = [
        '/home/pi/pwnagotchi',
        '/opt/pwnagotchi',
        '/usr/local/lib/python3.7/dist-packages/pwnagotchi'
    ]
    for dir in possible_dirs:
        if os.path.exists(dir):
            return dir
    return None

def find_new_files():
    home_dir = os.path.expanduser('~')
    for root, dirs, files in os.walk(home_dir):
        if 'gfx_hat' in dirs:
            return os.path.join(root, 'gfx_hat')
    return None

def backup_files(src_dir):
    backup_dir = os.path.join(src_dir, 'backup_gfx_hat')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    for file in os.listdir(src_dir):
        if file.endswith('.py') or file.endswith('.sh'):
            shutil.copy2(os.path.join(src_dir, file), backup_dir)
    print(f"Backup created in {backup_dir}")

def replace_files(src_dir, new_files_dir):
    for root, dirs, files in os.walk(new_files_dir):
        for file in files:
            if file.endswith('.py') or file.endswith('.sh'):
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(root, new_files_dir)
                dst_dir = os.path.join(src_dir, rel_path)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                dst_file = os.path.join(dst_dir, file)
                shutil.copy2(src_file, dst_file)
                print(f"Replaced {file}")

def set_permissions(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.py'):
                os.chmod(file_path, 0o644)
            elif file.endswith('.sh'):
                os.chmod(file_path, 0o755)

def update_config_toml(pwnagotchi_dir):
    config_path = os.path.join(pwnagotchi_dir, 'config.toml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = toml.load(f)
        
        config['ui']['display'] = {
            'type': 'gfxhat',
            'color': 'black'
        }
        
        with open(config_path, 'w') as f:
            toml.dump(config, f)
        print("Updated config.toml with GFX HAT display settings")
    else:
        print("config.toml not found. Please update it manually.")

def restart_pwnagotchi():
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'pwnagotchi'], check=True)
        print("Pwnagotchi service restarted successfully")
    except subprocess.CalledProcessError:
        print("Failed to restart Pwnagotchi service. You may need to reboot manually.")

def main():
    pwnagotchi_dir = find_pwnagotchi_dir()
    if not pwnagotchi_dir:
        print("Pwnagotchi directory not found. Please specify the correct path.")
        return

    new_files_dir = find_new_files()
    if not new_files_dir:
        print("New GFX HAT files directory not found. Please place the files in a 'gfx_hat' directory.")
        return

    print(f"Pwnagotchi directory: {pwnagotchi_dir}")
    print(f"New files directory: {new_files_dir}")

    confirm = input("Do you want to proceed with the update? (y/n): ")
    if confirm.lower() != 'y':
        print("Update cancelled.")
        return

    backup_files(pwnagotchi_dir)
    replace_files(pwnagotchi_dir, new_files_dir)
    set_permissions(pwnagotchi_dir)
    update_config_toml(pwnagotchi_dir)
    restart_pwnagotchi()

    print("Update completed. Please check if everything is working correctly.")

if __name__ == "__main__":
    main()
