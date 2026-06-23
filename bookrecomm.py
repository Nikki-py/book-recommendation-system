import requests
import re

API_KEY = "27451e015cc34a4a89df9d1e8d61f012"
BASE_URL = "https://api.bigbookapi.com"

def normalize(text):
    """Lowercase and strip punctuation, so 'Girl's' and 'Girls' match."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)  # remove anything that's not a letter/number/space
    return text.strip()


def title_similarity(a, b):
    """Return a rough similarity score between two normalized titles,
    based on how many words they share."""
    words_a = set(a.split())
    words_b = set(b.split())

    if not words_a or not words_b:
        return 0

    shared = words_a & words_b  # words present in both
    return len(shared) / max(len(words_a), len(words_b))


def search_book(title):
    url = f"{BASE_URL}/search-books"
    params = {"api-key": API_KEY, "query": title}

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("number", 0) == 0:
        return None

    target = normalize(title)

    best_match = None
    best_score = 0

    for result_group in data["books"]:
        book = result_group[0]
        score = title_similarity(target, normalize(book["title"]))
        print(f"DEBUG: '{book['title']}' -> score {score:.2f}")  # add this

        if score > best_score:
            best_score = score
            best_match = book

    print(f"DEBUG: best score was {best_score:.2f}")  # add this

    if best_match and best_score >= 0.6:
        return {"id": best_match["id"], "title": best_match["title"]}

    return None

def get_book_genres(book_id):
    """Fetch full info for a book and return its list of genres."""
    url = f"{BASE_URL}/{book_id}"
    params = {"api-key": API_KEY}

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("genres", [])


def search_by_genre(genre, exclude_title):
    """Search for books in a given genre, excluding the original book."""
    url = f"{BASE_URL}/search-books"
    params = {"api-key": API_KEY, "genres": genre}

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("number", 0) == 0:
        return []

    exclude_normalized = normalize(exclude_title)
    results = []
    seen_titles = set()

    for result_group in data["books"]:
        book = result_group[0]
        book_title_normalized = normalize(book["title"])

        # skip the book the user searched for, and any duplicate titles
        if book_title_normalized == exclude_normalized:
            continue
        if book_title_normalized in seen_titles:
            continue

        results.append(book["title"])
        seen_titles.add(book_title_normalized)

    return results


def recommend(title):
    found = search_book(title)

    if found is None:
        print("Sorry, couldn't find that exact book. Try checking the spelling.")
        return

    print(f"\nFound: {found['title']}")

    genres = get_book_genres(found["id"])

    if not genres:
        print("Couldn't find genre info for this book.")
        return

    genre = genres[0]  # just use the first/primary genre
    print(f"Genre: {genre}")

    recommendations = search_by_genre(genre, found["title"])

    if not recommendations:
        print("No genre-matched recommendations found.")
        return

    print("\nRecommendations:\n")
    for book_title in recommendations[:5]:
        print(book_title)


name = input("Please enter a book you liked: ")
recommend(name)