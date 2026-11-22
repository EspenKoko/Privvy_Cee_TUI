#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="PrivvyCee"
COMMAND_NAME="privvycee"
APP_SOURCE="$PWD/$APP_NAME"
APP_BINARY="$APP_SOURCE/$APP_NAME"

# Run the command; if it succeeds (exit code 0), exit the setup script immediately
if command -v "$COMMAND_NAME" >/dev/null 2>&1 && "$COMMAND_NAME"; then
    printf 'Privvycee already installed \n'
    exit 0
fi

fail() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

if ! command -v apt-get >/dev/null 2>&1; then
    fail "This setup script requires a Debian- or Ubuntu-based Linux distribution with apt-get."
fi

if [[ ! -d "$APP_SOURCE/_internal" || ! -f "$APP_BINARY" ]]; then
    fail "Run privvycee-setup.sh from the extracted bundle directory containing $APP_NAME/$APP_NAME."
fi

while true; do
    if ! read -r -p "Is this a headless system? Install dbus-x11? [y/n]: " response; then
        fail "No answer received. Run the setup again and enter y or n."
    fi

    case "$response" in
        [Yy])
            install_dbus_x11=true
            printf 'Skipping dbus-x11 package install.\n'
            break
            ;;
        [Nn])
            install_dbus_x11=false
            printf 'Adding dbus-x11 packages install.\n'
            break
            ;;
        *)
            printf 'Please enter y or n.\n'
            ;;
    esac
done

packages=(gnome-keyring)
if [[ "$install_dbus_x11" == true ]]; then
    packages+=(dbus-x11)
fi

if [[ "$EUID" -eq 0 ]]; then
    apt-get update
    apt-get install -y "${packages[@]}"
else
    command -v sudo >/dev/null 2>&1 || fail "sudo is required to install system packages."
    sudo apt-get update
    sudo apt-get install -y "${packages[@]}"
fi

if [[ "$install_dbus_x11" == true ]]; then
    printf 'dbus-x11 was installed. Ensure GNOME Keyring is started and unlocked before saving credentials.\n'
fi

install_dir="$HOME/.local/opt/privvycee"
bin_dir="$HOME/.local/bin"
app_binary="$install_dir/$APP_NAME"

mkdir -p "$install_dir" "$bin_dir" "$HOME/.local/share/keyrings"
chmod u+x "$app_binary"
ln -sfn "$app_binary" "$bin_dir/$COMMAND_NAME"

source ~/.profile

printf "\n Setup complete, you may run the Privvycee TUI with the command '%s'\n" "$COMMAND_NAME"
