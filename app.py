from flask import Flask, render_template, request
import pickle
import numpy as np
from fuzzywuzzy import process

popular_df = pickle.load(open('popular.pkl' , 'rb'))
pivot = pickle.load(open('pivot.pkl' , 'rb'))
books = pickle.load(open('books.pkl' , 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl' , 'rb'))


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', 
                           book_isbn = list(popular_df['ISBN'].values),
                           book_name = list(popular_df['Book-Title'].values),
                           book_author = list(popular_df['Book-Author'].values),
                           book_img = list(popular_df['Image-URL-M'].values),
                           book_year = list(popular_df['Year-Of-Publication'].values),
                           book_votes = list(popular_df['Num_Ratings'].values),
                           book_rating = list(popular_df['Avg_Ratings'].values),
                           )



# Function to find the closest matches for a book title
def get_closest_book_titles(user_input, book_titles, n=5):
    user_input_lower = user_input.lower()
    matches = process.extract(user_input_lower, book_titles, limit=n)
    return [match[0] for match in matches]

@app.route('/rec')
def recommend_ui():
    return render_template('rec.html')

@app.route('/rec_books' , methods = ['POST'])
def recommend():
    user_input = request.form.get('user_input')
    # index = np.where(pivot.index == user_input)[0][0]

    book_titles = pivot.index.tolist()

    # Find closest matches to the user's input
    closest_titles = get_closest_book_titles(user_input, book_titles)

    # If no close matches found, return an empty list
    if not closest_titles:
        return render_template('rec.html', data=[])

    # Use the first closest match for recommendation
    index = np.where(pivot.index == closest_titles[0])[0][0]


    # this means that first book ka dusri book ke respect me similarity score ye hai
    similar_items = sorted(list(enumerate(similarity_scores[index])), key = lambda x:x[1], reverse = True)[1:9]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pivot.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('rec.html' , data=data )

if __name__ == '__main__':
    app.run(debug=True)