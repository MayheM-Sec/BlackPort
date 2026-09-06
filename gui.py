"""
MayheM-Sec Added

Compatibility launcher for the BlackPort local graphical interface.
The MayheM-Sec fork uses gui_server_v3.py for TCP, SYN, UDP, Mixed scans,
scan history, and local report viewing.
"""

from gui_server_v3 import main


if __name__ == "__main__":
    main()
