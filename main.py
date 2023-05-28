# Narazie mam: podstawowy interfejs, funkcje która odczytuje pliki z katalogu i wyjscie
# Update: dodana funkcja obliczania skrótu pliku i obliczania jej dla plikow we wskazanym katalogu
# Update: Poprawienie wyboru katalogu do badania i wstepne dodanie konfiguracji

import PySimpleGUI as sg
import os
import hashlib

# Ustalanie obecnego katalogu jako wartość domyślna
sciezka_katalogu_domyslna = os.getcwd()


# Obliczanie funkcji skrótu
def oblicz_skrót(plik):
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
    zawartosc = odczytaj_katalog(sciezka)
    for element in zawartosc:
        if os.path.isfile(element):  # Sprawdź tylko pliki
            nazwa_pliku = os.path.basename(element)
            skrot = oblicz_skrót(element)
            print("Plik:", nazwa_pliku)
            print("Ścieżka:", element)
            print("Skrót SHA256:", skrot)
            print("------------------------------")


# Definicja układu interfejsu
layout = [
    [sg.Text("Witaj w aplikacji do weryfikacji integralności systemu plików!")],
    # [sg.Text("Ścieżka katalogu:", size=(15, 1)),
    #  sg.InputText(default_text=sciezka_katalogu_domyslna, key="sciezka_katalogu")],
    [sg.Button("Badaj katalog"), sg.Button("Konfiguracja"), sg.Button("Wyjście")],
    [sg.Output(size=(60, 10), key="output")]  # Element Output dla wyświetlania tekstu
]

# Utworzenie okna
window = sg.Window("Aplikacja do weryfikacji integralności systemu plików", layout)

# Pętla zdarzeń
while True:
    event, values = window.read()

    # Obsługa zdarzenia zamknięcia okna
    if event == sg.WINDOW_CLOSED or event == "Wyjście":
        break

    # Narazie oblicza funkcje skrótów dla wszystkich plików w wybranym katalogu
    # Poprawiony wybór katalogu
    elif event == "Badaj katalog":
        badanie_layout = [
            [sg.Text("Badanie")],
            [sg.Text("Wybierz katalog do badania:", size=(20, 1)), sg.FolderBrowse(key="sciezka_katalogu")],
            [sg.Button("Badaj"), sg.Button("Powrot")],
            [sg.Output(size=(60, 10), key="output")]  # Element Output dla wyświetlania tekstu
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
    # Ustawienie konfiguracji badania katalogu, ale to trzeba pozniej wszystko do bazy danych
    elif event == "Konfiguracja":
        konfiguracja_layout = [
            [sg.Text("Konfiguracja")],
            [sg.Text("Wybierz katalog do badania:", size=(20, 1)), sg.FolderBrowse(key="konfiguracja_katalogu")],
            [sg.Button("Zapisz"), sg.Button("Anuluj")]
        ]

        konfiguracja_window = sg.Window("Konfiguracja", konfiguracja_layout)

        while True:
            konfiguracja_event, konfiguracja_values = konfiguracja_window.read()

            if konfiguracja_event == sg.WINDOW_CLOSED or konfiguracja_event == "Anuluj":
                break

            elif konfiguracja_event == "Zapisz":
                sciezka_katalogu_domyslna = konfiguracja_values["konfiguracja_katalogu"]
                sg.popup("Zapisano konfigurację")

        konfiguracja_window.close()

# Zamknięcie okna i zakończenie programu
window.close()
