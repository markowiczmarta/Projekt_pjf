# Poprawic wyglad graficzny
# Pozabezpieczac i testowac

import sys
import threading
import PySimpleGUI as sg
import os
import hashlib
import sqlite3
from datetime import datetime
import schedule

# Ustalanie obecnego katalogu jako wartość domyślna
sciezka_katalogu_domyslna = os.getcwd()


# Obliczanie funkcji skrótu
def oblicz_skrot(plik):
    with open(plik, "rb") as f:
        dane = f.read()
        skrot = hashlib.sha256(dane).hexdigest()
    return skrot


# Funkcja do pobierania zawartości katalogu
def odczytaj_katalog(sciezka):
    zawartosc = []
    for sciezka_katalogu, podkatalogi, pliki in os.walk(sciezka):
        for podkatalog in podkatalogi:
            zawartosc.append(os.path.join(sciezka_katalogu, podkatalog))
        for plik in pliki:
            zawartosc.append(os.path.join(sciezka_katalogu, plik))
    return zawartosc


def badaj_katalog(sciezka):
    conn = sqlite3.connect("bazadanych.db")
    c = conn.cursor()
    zawartosc = odczytaj_katalog(sciezka)
    for element in zawartosc:
        if os.path.isfile(element):  # Sprawdź tylko pliki
            nazwa_pliku = os.path.basename(element)
            skrot = oblicz_skrot(element)
            print("Plik:", nazwa_pliku)
            print("Ścieżka:", element)
            print("Skrót SHA256:", skrot)
            print("------------------------------")
            cre_date = datetime.fromtimestamp(os.path.getctime(element))
            mod_date = datetime.fromtimestamp(os.path.getmtime(element))
            check_date = datetime.now()

            # sprawdz czy plik istnieje juz w bazie
            c.execute("SELECT file_id FROM File WHERE path = ?", (element,))
            result = c.fetchone()

            if result is None:
                c.execute("INSERT INTO File (path, name, cre_date, mod_date, hash, check_date) VALUES ( ?, ?, ?, ?, "
                          "?, ?)", (element, nazwa_pliku, cre_date, mod_date, skrot, check_date))
                c.execute("INSERT INTO Change_log (file_id, change_type, change_date) VALUES ( ?, ?, ?)",
                          (c.lastrowid, "NEW", datetime.now()))
            else:
                file_id = result[0]
                c.execute("SELECT hash FROM File WHERE file_id = ?", (file_id,))
                prev_hash = c.fetchone()[0]
                if prev_hash != skrot:
                    print("Zmiana w pliku:", nazwa_pliku)
                    c.execute("UPDATE File SET hash = ?, mod_date = ?, check_date = ? WHERE file_id = ?",
                              (skrot, mod_date, check_date, file_id))
                    c.execute("INSERT INTO Change_log (file_id, change_type, change_date) VALUES ( ?, ?, ?)",
                              (file_id, "MODIFIED", datetime.now()))
                else:
                    print("Brak zmian w pliku:", nazwa_pliku)
                    c.execute("UPDATE File SET check_date = ? WHERE file_id = ?", (check_date, file_id))
            conn.commit()
    conn.close()


def badaj_katalog_okresowo(sciezka, czestotliwosc, running_flag):
    schedule.every(czestotliwosc).seconds.do(badaj_katalog, sciezka)
    while running_flag.is_set():
        schedule.run_pending()


# layout = [
#     [sg.Text("Witaj w aplikacji do weryfikacji integralności systemu plików!")],
#     [sg.Button("Badaj katalog"), sg.Button("Konfiguracja"), sg.Button("Wyjście")],
#     [sg.Button("Info")],
#     [sg.Output(size=(60, 10), key="output")]  # Element Output dla wyświetlania tekstu
# ]
layout = [
    [sg.Text("Witaj w aplikacji do weryfikacji integralności systemu plików!", font=("Helvetica", 16), justification="center")],
    [sg.Button("Badaj katalog", size=(10, 2), font=("Helvetica", 12)),
     sg.Button("Konfiguracja", size=(10, 2), font=("Helvetica", 12)),
     sg.Button("Info", size=(10, 2), font=("Helvetica", 12))],
    [sg.Button("Wyjscie", size=(10, 2), font=("Helvetica", 12))],
    [sg.VerticalSeparator()],

]


# Utworzenie okna
window = sg.Window("Aplikacja do weryfikacji integralności systemu plików", layout)

running = True
bg_thread = None
running_flag = threading.Event()
running_flag.set()
while running:
    event, values = window.read()

    # Obsługa zdarzenia zamknięcia okna
    if event == sg.WINDOW_CLOSED or event == "Wyjscie":
        running = False
        if bg_thread:
            running_flag.clear()
            bg_thread.join()  # Poczekaj na zakończenie wątku

    elif event == "Badaj katalog":
        badanie_layout = [
            [sg.Text("Badanie", font=("Helvetica", 16), justification="center")],
            [sg.Text("Wybierz katalog do badania:", font=("Helvetica", 12), size=(20, 1)),
             sg.FolderBrowse(key="sciezka_katalogu", font=("Helvetica", 12))],
            [sg.Button("Badaj", size=(8, 1), font=("Helvetica", 10)),
             sg.Button("Powrot", size=(8, 1), font=("Helvetica", 10))],
            [sg.VerticalSeparator()],
            [sg.Output(size=(60, 10), key="output", font=("Helvetica", 10))]  # Element Output dla wyświetlania tekstu
        ]

        badanie_window = sg.Window("Badanie", badanie_layout)
        while True:
            badanie_event, badanie_values = badanie_window.read()

            if badanie_event == sg.WINDOW_CLOSED or badanie_event == "Powrot":
                break

            elif badanie_event == "Badaj":
                sciezka_katalogu = badanie_values["sciezka_katalogu"]
                window["output"].update("")  # Wyczyszczenie pola wyjścia przed wypisaniem nowych danych
                window["output"].print(f"Badanie integralności katalogu: {sciezka_katalogu}")
                badaj_katalog(sciezka_katalogu)

        badanie_window.close()

    # Obsługa zdarzenia "Konfiguracja"
    # Zrobilam aby ustawienie bylo w sekundach zeby latwiej bylo zaprezentowac
    elif event == "Konfiguracja":
        conn = sqlite3.connect("bazadanych.db")
        c = conn.cursor()
        konfiguracja_layout = [
            [sg.Text("Konfiguracja", font=("Helvetica", 16), justification="center")],
            [sg.Text("Wybierz katalog do badania:", font=("Helvetica", 12), size=(20, 1)),
             sg.FolderBrowse(key="konfiguracja_katalogu", font=("Helvetica", 12))],
            [sg.Text("Wybierz częstotliwość badania (w minutach):", font=("Helvetica", 12), size=(20, 1)),
             sg.InputText(key="czestotliwosc", font=("Helvetica", 12))],
            [sg.Button("Zapisz", size=(8, 1), font=("Helvetica", 10)),
             sg.Button("Anuluj", size=(8, 1), font=("Helvetica", 10))]
        ]

        konfiguracja_window = sg.Window("Konfiguracja", konfiguracja_layout)

        while True:
            konfiguracja_event, konfiguracja_values = konfiguracja_window.read()

            if konfiguracja_event == sg.WINDOW_CLOSED or konfiguracja_event == "Anuluj":
                break

            elif konfiguracja_event == "Zapisz":
                sciezka_katalogu = konfiguracja_values["konfiguracja_katalogu"]
                czestotliwosc = int(konfiguracja_values["czestotliwosc"])
                window["output"].update("")  # Wyczyszczenie pola wyjścia przed wypisaniem nowych danych
                try:
                    # Sprawdzenie, czy konfiguracja dla danego katalogu już istnieje
                    c.execute("SELECT * FROM Configuration WHERE dir = ?", (sciezka_katalogu,))
                    existing_config = c.fetchone()
                    if existing_config:
                        # Aktualizacja istniejącej konfiguracji
                        c.execute("UPDATE Configuration SET scan_freq = ? WHERE dir = ?",
                                  (czestotliwosc, sciezka_katalogu))
                        conn.commit()
                        sg.popup("Zaktualizowano konfigurację")
                    else:
                        # Dodanie nowej konfiguracji
                        c.execute("INSERT INTO Configuration (dir, scan_freq) VALUES (?, ?)",
                                  (sciezka_katalogu, czestotliwosc))
                        conn.commit()
                        sg.popup("Zapisano konfigurację")

                    if bg_thread is None or not bg_thread.is_alive():
                        running_flag.set()
                        bg_thread = threading.Thread(target=badaj_katalog_okresowo,
                                                     args=(sciezka_katalogu, czestotliwosc, running_flag))
                        bg_thread.daemon = True
                        bg_thread.start()

                except sqlite3.Error as e:
                    print("Błąd przy zapisie konfiguracji:", e)

        konfiguracja_window.close()
        conn.close()
    elif event == "Info":
        conn = sqlite3.connect("bazadanych.db")
        c = conn.cursor()
        info_layout = [
            [sg.Text("Informacje o biezacym stanie plikow", font=("Helvetica", 16), justification="center")],
            [sg.Text("Wybierz katalog:", font=("Helvetica", 12), size=(20, 1)),
             sg.FolderBrowse(key="info_katalog", font=("Helvetica", 12))],
            [sg.Button("Ok", size=(8, 1), font=("Helvetica", 10)),
             sg.Button("Powrot", size=(8, 1), font=("Helvetica", 10))]
        ]

        info_window = sg.Window("Informacje", info_layout)
        table_window = None
        while True:
            event, values = info_window.read()
            if event == sg.WINDOW_CLOSED or event == "Powrot":
                break
            elif event == "Ok":
                sciezka_katalogu = values["info_katalog"]
                c.execute("""
                    SELECT File.path, File.name, File.cre_date, File.mod_date, File.check_date, File.hash, 
                        CASE WHEN File.check_date < Change_log.change_date THEN Change_log.change_type ELSE '' END AS change_type,
                        CASE WHEN File.check_date < Change_log.change_date THEN Change_log.change_date ELSE '' END AS change_date
                    FROM File
                    LEFT JOIN Change_log ON File.file_id = Change_log.file_id
                    WHERE File.path LIKE ?
                    """, ("%" + sciezka_katalogu + "%",))
                results = c.fetchall()
                if results:
                    headings = [description[0] for description in c.description]
                    results_as_list = [list(result) for result in results]  # Przekształć krotki na listy
                    layout = [
                        [sg.Table(values=results_as_list, headings=headings, max_col_width=25, auto_size_columns=True,
                                  justification='left', num_rows=20, key="table")],
                        [sg.Button("Powrot")]
                    ]
                    table_window = sg.Window("Informacje", layout)
                    while True:
                        table_event, table_values = table_window.read()
                        if table_event == sg.WINDOW_CLOSED or table_event == "Powrot":
                            break
                    table_window.close()
                else:
                    sg.popup("Nie znaleziono plików")
            info_window.close()

window.close()
sys.exit()
