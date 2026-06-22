import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

books = pd.read_csv("book_list.csv")
books = books.loc[:, ~books.columns.str.contains('^Unnamed')]

books["Name"] = books["Name"].str.lower()
books["Genre"] = books["Genre"].str.lower()
books["Author"] = books["Author"].str.lower()

read_books = books[books["Read"] == "Yes"]
unread_books = books[books["Read"] == "No"]

print("total books : ",len(books))
print("read books : ",len(read_books))
print("unread books : ",len(unread_books))

books["Features"]= books["Genre"]+" "+books["Author"]

vectorizer = CountVectorizer()

feature_matrix = vectorizer.fit_transform(
    books["Features"]
)

similarity_matrix = cosine_similarity(feature_matrix)

name = input("please enter the book you liked : ").lower()
matching_books = books[
    books["Name"] == name
]

if matching_books.empty:
    print("Book not found")
    exit()

book_index = matching_books.index[0]

similar_scores = list(enumerate(similarity_matrix[book_index]))

similar_scores = sorted(
    similar_scores,
    key=lambda x: x[1],
    reverse=True
)

print("\nRecommendations:\n")

count = 0

for i in similar_scores:
    book = books.iloc[i[0]]
    if book["Read"] == "No":
        print(book["Name"])
        count += 1
    if count == 5:
        break
