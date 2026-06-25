import requests
import re

GOOGLE_API_KEY = "AIzaSyCpC8X7BS44SiK85RxUMCN0-B7VEc9Q_wg"
BIGBOOK_API_KEY = "27451e015cc34a4a89df9d1e8d61f012"
BIGBOOK_BASE_URL = "https://api.bigbookapi.com"

VALID_GENRES = {
    "action", "adventure", "anthropology", "astronomy", "archaeology",
    "architecture", "art", "aviation", "biography", "biology", "business",
    "chemistry", "children", "classics", "contemporary", "cookbook",
    "crafts", "crime", "dystopia", "economics", "education", "engineering",
    "environment", "erotica", "essay", "fairy_tales", "fantasy", "fashion",
    "feminism", "fiction", "finance", "folklore", "food", "gaming",
    "gardening", "geography", "geology", "graphic_novel", "health",
    "historical", "historical_fiction", "history", "horror", "how_to",
    "humor", "inspirational", "journalism", "law", "literary_fiction",
    "literature", "magical_realism", "manga", "martial_arts",
    "mathematics", "medicine", "medieval", "memoir", "mystery",
    "mythology", "nature", "nonfiction", "novel", "occult", "paranormal",
    "parenting", "philosophy", "physics", "picture_book", "poetry",
    "politics", "programming", "psychology", "reference", "relationships",
    "religion", "romance", "science_and_technology", "science_fiction",
    "self_help", "short_stories", "society", "sociology", "space",
    "spirituality", "sports", "text_book", "thriller", "travel",
    "true_crime", "war", "writing", "young_adult"
}


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def title_similarity(a, b):
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0
    shared = words_a & words_b
    return len(shared) / len(words_a)


def get_genre_from_google(title):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": title, "maxResults": 1, "key": GOOGLE_API_KEY}

    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data:
        return None

    book = data["items"][0]["volumeInfo"]
    categories = book.get("categories", [])

    if not categories:
        return None

    raw_category = normalize(categories[0])
    words = raw_category.split()

    for word in words:
        if word in VALID_GENRES:
            return word

    return None


def search_book(title):
    """Search Big Book API for a title, picking the best-scoring match."""
    url = f"{BIGBOOK_BASE_URL}/search-books"
    params = {"api-key": BIGBOOK_API_KEY, "query": title}

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
        if score > best_score:
            best_score = score
            best_match = book

    if best_match and best_score >= 0.5:
        return {"id": best_match["id"], "title": best_match["title"]}

    return None


def searchbygenre(genre, exclude_title):
    """Search Big Book API for books in a specific genre."""
    url = f"{BIGBOOK_BASE_URL}/search-books"
    params = {"api-key": BIGBOOK_API_KEY, "genres": genre}

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
    confirm = input("Is this the book you meant? (y/n): ").strip().lower()

    if confirm != "y":
        print("Okay, skipping recommendations. Try rephrasing your search.")
        return

    genre = get_genre_from_google(found["title"])

    if genre is None:
        print("Couldn't determine a genre for this book.")
        return

    print(f"Genre: {genre}")

    recommendations = searchbygenre(genre, found["title"])

    if not recommendations:
        print("No genre-matched recommendations found.")
        return

    print("\nRecommendations:\n")
    for book_title in recommendations[:5]:
        print(book_title)


name = input("Please enter a book you liked: ")
recommend(name)