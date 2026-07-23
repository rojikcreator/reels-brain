"""Importne Instagram session z prehliadaca do Instaloaderu.

Pouzitie:  py tools\import_browser_session.py

V prehliadaci, kde si prihlaseny na instagram.com:
  F12 -> zalozka Application (Chrome) / Storage (Firefox)
  -> Cookies -> https://www.instagram.com
  -> najdi cookie `sessionid` a skopiruj jej HODNOTU (celu).

Hodnotu vloz az po vyzve tohto skriptu (vstup je skryty).
sessionid je kluc od tvojho uctu - NIKDY ju nevkladaj do chatu ani nikomu neposielaj.
"""
from getpass import getpass

import instaloader

sessionid = getpass("Vloz hodnotu cookie sessionid (vstup je skryty): ").strip()
if not sessionid:
    raise SystemExit("Prazdny vstup - nic sa neulozilo.")

L = instaloader.Instaloader()
L.context._session.cookies.set("sessionid", sessionid, domain=".instagram.com")
username = L.test_login()
if not username:
    raise SystemExit("Cookie neplati - skontroluj, ci si skopiroval celu hodnotu sessionid.")
L.context.username = username
L.save_session_to_file()
print(f"Hotovo - session ulozena pre '{username}' (nahradila povodnu login session).")
