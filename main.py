# Narazie mam: podstawowy interfejs, funkcje która odczytuje pliki z katalogu i wyjscie
# Update: dodana funkcja obliczania skrótu pliku i obliczania jej dla plikow we wskazanym katalogu


import PySimpleGUI as sg
import os
import hashlib

# Ustalanie obecnego katalogu jako wartość domyślna
sciezka_katalogu_domyslna = os.getcwd()


# Obliczanie funkcji skrotu
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
    [sg.Text("Ścieżka katalogu:", size=(15, 1)),
     sg.InputText(default_text=sciezka_katalogu_domyslna, key="sciezka_katalogu")],
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

    # Narazie oblicza funkcje skrotu dla wszystkich plikow w wybranym katalogu
    elif event == "Badaj katalog":
        sciezka_katalogu = values["sciezka_katalogu"]
        window["output"].update("")  # Wyczyszczenie pola wyjścia przed wypisaniem nowych danych
        window["output"].print(f"Badanie integralności katalogu: {sciezka_katalogu}")
        badaj_katalog(sciezka_katalogu)

    # Obsługa zdarzenia "Konfiguracja"
    elif event == "Konfiguracja":
        sciezka_katalogu_domyslna = values["sciezka_katalogu"]
        # Kod do obsługi konfiguracji

# Zamknięcie okna i zakończenie programu
window.close()
