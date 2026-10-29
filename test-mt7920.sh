#!/bin/bash
# Post-install test for SimpleMtkWlan (MT7920) on macOS.
# Run from the folder that contains SimpleMtkWlan.kext:
#   bash test-mt7920.sh
# Does NOT touch OpenCore. Remove with: sudo rm -rf "/Library/Application Support/MtkWlan" && reboot

set -u
KEXT_NAME="SimpleMtkWlan.kext"
DEST="/Library/Application Support/MtkWlan"

echo "== macOS version"
sw_vers -productVersion

echo "== Wi-Fi card on PCI (expect 14c3:7920)"
ioreg -l -w0 | grep -i "pci14c3" | head -n 3 || true
ioreg -l -w0 | grep -i -E "\"vendor-id\"|\"device-id\"" | head -n 4 || true

if [ ! -d "$KEXT_NAME" ]; then
  echo "ERROR: $KEXT_NAME not found in $(pwd)"
  exit 1
fi

echo "== Copying kext to $DEST"
sudo mkdir -p "$DEST"
sudo rm -rf "$DEST/$KEXT_NAME"
sudo cp -R "$KEXT_NAME" "$DEST/"
sudo chown -R root:wheel "$DEST/$KEXT_NAME"

echo "== Loading kext"
if sudo kmutil load -p "$DEST/$KEXT_NAME"; then
  echo "Load OK"
else
  echo "Load failed. If it says 'not approved', open System Settings > Privacy & Security, allow the kext, reboot, then run this script again."
fi

echo "== Loaded kexts (SimpleMtkWlan / mtk)"
kextstat 2>/dev/null | grep -i -E "mtk|simplemtk" || echo "none listed"

echo "== Network interfaces"
ifconfig -a | grep -E "^en|status|media" | head -n 30

echo "== Driver log (last 5 minutes)"
log show --last 5m --predicate 'process == "kernel"' --info 2>/dev/null | grep -i -E "mwx|mtk|SimpleMtk" | tail -n 40 || echo "no log lines"
