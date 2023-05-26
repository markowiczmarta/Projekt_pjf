# Narazie mam: podstawowy interfejs, funkcje która odczytuje pliki z katalogu i wyjscie

import PySimpleGUI as sg
import os

# Ustalanie obecnego katalogu jako wartość domyślna
sciezka_katalogu_domyslna = os.getcwd()


# Funkcja do pobierania zawartości katalogu
def odczytaj_katalog(sciezka):
    zawartosc = []
    for sciezka_katalogu, podkatalogi, pliki in os.walk(sciezka):
        for podkatalog in podkatalogi:
            zawartosc.append(os.path.join(sciezka_katalogu, podkatalog))
        for plik in pliki:
            zawartosc.append(os.path.join(sciezka_katalogu, plik))
    return zawartosc


# Definicja układu interfejsu
layout = [
    [sg.Text("Witaj w aplikacji do weryfikacji integralności systemu plików!")],
    [sg.Text("Ścieżka katalogu:", size=(15, 1)),
     sg.InputText(default_text=sciezka_katalogu_domyslna, key="sciezka_katalogu")],
    [sg.Button("Wyświetl zawartość"), sg.Button("Konfiguracja"), sg.Button("Wyjście")],
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

    # Obsługa zdarzenia "Wyświetl zawartość"
    elif event == "Wyświetl zawartość":
        sciezka_katalogu = values["sciezka_katalogu"]
        # Kod do wyświetlenia zawartości katalogu w polu wyjścia
        window["output"].update("")  # Wyczyszczenie pola wyjścia przed wypisaniem nowych danych
        window["output"].print(f"Zawartość katalogu: {sciezka_katalogu}")
        zawartosc = odczytaj_katalog(sciezka_katalogu)
        for element in zawartosc:
            nazwa_pliku = os.path.basename(element)
            window["output"].print(nazwa_pliku)

    # Obsługa zdarzenia "Konfiguracja"
    elif event == "Konfiguracja":
        sciezka_katalogu_domyslna = values["sciezka_katalogu"]
        # Kod do obsługi konfiguracji

# Zamknięcie okna i zakończenie programu
window.close()