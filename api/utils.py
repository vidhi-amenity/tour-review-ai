from api.models import SOURCE_STREAM, Notification, STREAM_CHOICES
from django.db.models import Count
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pycountry
import json
import matplotlib
matplotlib.use('agg')


def search_by_factor(reviews, reviews_before, search_factor):
    reviews = reviews.values(search_factor).annotate(total_reviews=Count(search_factor))
    if reviews_before is not None:
        reviews_before = reviews_before.values(search_factor).annotate(total_reviews=Count(search_factor))

    data = []
    for r in reviews:
        if reviews_before is not None:
            r['total_previous_reviews'] = next((p_rev['total_reviews'] for p_rev in reviews_before if r[search_factor] == p_rev[search_factor]), 0)
        else:
            r['total_previous_reviews'] = 0

        if search_factor == 'source_stream':
            r[search_factor] = SOURCE_STREAM[r[search_factor]]['name']
        elif search_factor == 'country_code':
            try:
                country = pycountry.countries.get(alpha_2=r[search_factor])
                r[search_factor] = country.name
            except:
                continue
        data.append(r)

    return data

def search_by_keywords(reviews, reviews_before, search_factor):
    stop_words = set(stopwords.words('english'))
    wordnet_lemmatizer = WordNetLemmatizer()

    # Get all reviews with positive or negative sentiment
    reviews = reviews.exclude(places=None)
    if reviews_before is not None:
        reviews_before = reviews_before.exclude(places=None)

    data = []

    # Initialize frequency counters for positive and negative reviews
    word_freq = Counter()
    word_freq_before = Counter()

    for review in reviews:
        words = preprocess_text(review.places, stop_words, wordnet_lemmatizer)
        word_freq.update(words)

    if reviews_before is not None:
        for review in reviews_before:
            words = preprocess_text(review.places, stop_words, wordnet_lemmatizer)
            word_freq_before.update(words)

    for item in word_freq:
        data.append({
            'keywords': item,
            'total_reviews': word_freq[item],
            'total_previous_reviews': word_freq_before.get(item, 0) if reviews_before is not None else 0,
        })
    return data



def preprocess_text(places, stop_words, wordnet_lemmatizer):
    places = json.loads(places)
    # # Remove stopwords
    words = [word['name'] for word in places if word['name'] not in stop_words]
    # # Lemmatize words
    words = [wordnet_lemmatizer.lemmatize(word) for word in words]
    return words


def create_notification(client, status, text, source_stream):
    stream = get_streams(source_stream)
    text = stream.capitalize() + text
    Notification.objects.create(
        user=client,
        client_field=client,
        status=status, text=text
    )

def get_streams(id_):
    matches = [text for (item_id, text) in STREAM_CHOICES if item_id == int(id_)]
    return matches[0] if matches else None