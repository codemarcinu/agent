# 🍽️ Meal Planner App

Aplikacja webowa do zarządzania produktami spożywczymi i generowania sugestii posiłków przy użyciu lokalnego modelu AI (Ollama).

## 🚀 Jak uruchomić?

1.  **Wymagania wstępne:**
    *   Python 3.8+
    *   PostgreSQL (uruchomiony na porcie 5432)
    *   Ollama (uruchomiony na porcie 11434)

2.  **Instalacja:**
    ```bash
    cd meal-planner-app
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Konfiguracja:**
    *   Skopiuj `.env.example` do `.env`.
    *   Ustaw dane do bazy danych i Ollama w pliku `.env`.
    *   Domyślny model AI to `bielik-11b-v2.3-instruct:Q4_K_M`.

4.  **Uruchomienie:**
    ```bash
    python app.py
    ```
    Otwórz przeglądarkę pod adresem: [http://localhost:5000](http://localhost:5000)

## ⚙️ Funkcje

*   **Produkty:** Dodawanie, usuwanie i przeglądanie produktów.
*   **Sugestie AI:**
    *   Generowanie pomysłu na posiłek.
    *   Tworzenie jadłospisu na 7 dni.
    *   Sugestie listy zakupów.
*   **Ustawienia:** Konfiguracja połączeń i wybór modelu AI bezpośrednio z interfejsu.

## 📝 Uwagi

*   Upewnij się, że masz utworzoną bazę danych `meal_planner` oraz użytkownika `meal_user` w PostgreSQL.
*   Jeśli model Ollama nie pojawia się na liście, sprawdź czy Ollama działa (`curl http://localhost:11434/api/tags`).
