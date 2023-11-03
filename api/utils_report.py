import json

from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from rest_framework import generics
from api.serializers import ReviewSerializer, RespondReviewSerializer
from api.models import Review, SOURCE_STREAM, INSTAGRAM, FACEBOOK, GOOGLE, LINKEDIN, STREAM_CHOICES
from django_filters import rest_framework as filters
from api.filters import ReviewFilter
from django.conf import settings
import calendar
from rest_framework import status
from streams.apis.facebook_apis import reply_facebook_comment, reply_instagram_comment
from django.db.models import Avg
from django.db.models import Count, Q, Case, When, Value, CharField, F
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import nltk
import pycountry
nltk.download('wordnet')
nltk.download('stopwords')


def summary_evolution(client, start_date, end_date, tour_id, country_id, city_id, source_stream):
    for stream_id, stream_name in STREAM_CHOICES:
        if stream_name == source_stream:
            source_stream = stream_id
            break

    if not start_date:
        start_date = date.today() - timedelta(days=31)
    else:
        start_date = date.fromisoformat(start_date)

    if not end_date:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end_date)

    if type(start_date) == datetime:
        start_date = start_date.date()

    if start_date < client.date_joined.date():
        start_date = client.date_joined.date()

    daily_review_stats = []

    reviews = Review.objects.filter(client=client)
    if source_stream != 'all':
        reviews = reviews.filter(source_stream=source_stream)

    if tour_id and tour_id != 'all':
        tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
        if tour_ids:
            reviews = reviews.filter(tour_id__in=tour_ids)

    if country_id and country_id != 'all':
        country_ids = [int(id) for id in country_id.strip('[]').split(',')]
        if country_ids:
            reviews = reviews.filter(country_id__in=country_ids)

    if city_id and city_id != 'all':
        reviews = reviews.filter(city_id=city_id)

    while start_date <= end_date:
        date_reviews = reviews.filter(date=start_date)

        positive_reviews = date_reviews.filter(rating=5).count()
        passive_reviews = date_reviews.filter(rating=4).count()
        negative_reviews = date_reviews.filter(rating__lte=3).count()

        # value = positive_reviews - (negative_reviews + passive_reviews)
        value = positive_reviews - (negative_reviews)

        daily_review_stats.append({
            "date": start_date.strftime("%Y-%m-%d"),
            "value": value
        })

        start_date += timedelta(days=1)
    return daily_review_stats

def summary_evolution_total(client, start_date, end_date, tour_id, country_id, city_id, source_stream):
    for stream_id, stream_name in STREAM_CHOICES:
        if stream_name == source_stream:
            source_stream = stream_id
            break

    if not start_date:
        start_date = date.today() - timedelta(days=31)
    else:
        start_date = date.fromisoformat(start_date)
    if not end_date:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end_date)

    if type(start_date) == datetime:
        start_date = start_date.date()

    if start_date < client.date_joined.date():
        start_date = client.date_joined.date()

    reviews = Review.objects.filter(client=client, date__range=(start_date, end_date)).exclude(sentiment=None)
    if source_stream != 'all':
        reviews = reviews.filter(source_stream=source_stream)

    if tour_id and tour_id != 'all':
        tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
        if tour_ids:
            reviews = reviews.filter(tour_id__in=tour_ids)

    if country_id and country_id != 'all':
        country_ids = [int(id) for id in country_id.strip('[]').split(',')]
        if country_ids:
            reviews = reviews.filter(country_id__in=country_ids)

    if city_id and city_id != 'all':
        reviews = reviews.filter(city_id=city_id)

    sentiment_counts = (
        reviews
        .values('rating')
        .annotate(total=Count('id'))
        .order_by('rating')
    )

    result_list = []
    negative_total = 0
    positive_total = 0
    passive_total = 0

    sentiment = ''
    lowScore = 0
    highScore = 0
    color = ''
    for count in sentiment_counts:
        if count['rating'] == 5:
            sentiment = 'Positive'
            highScore = passive_total + count['total']
            lowScore = passive_total
            color = "#0f9747"
            positive_total = count['total']
        elif count['rating'] == 4:
            sentiment = 'Passive'
            highScore = count['total']
            lowScore = 0
            color = "#fdae19"
            passive_total = count['total']
        elif count['rating'] <= 3:
            sentiment = 'Negative'
            highScore = 0
            lowScore = 0 - count['total']
            color = "#ee1f25"
            negative_total = count['total']
        result_list.append({
            'sentiment': sentiment,
            'lowScore': lowScore,
            'highScore': highScore,
            'color': color
        })

    if negative_total == 0:
        sentiment_percentage = 0
    else:
        sentiment_ratio = positive_total / (positive_total + negative_total)
        sentiment_percentage = sentiment_ratio * 100

    tot_reviews = positive_total + negative_total + passive_total

    positive_percentual = passive_percentual = negative_percentual = 0

    if tot_reviews != 0:
        if positive_total != 0:
            positive_percentual = (positive_total / tot_reviews) * 100
        elif passive_total != 0:
            passive_percentual = (passive_total / tot_reviews) * 100
        elif negative_total != 0:
            negative_percentual = (negative_total / tot_reviews) * 100

    res = {
        'min': 0 - negative_total,
        'max': positive_total + passive_total,
        'score': sentiment_percentage,
        'gradingData': [
            {
                'sentiment': 'Positive',
                'lowScore': positive_percentual,
                'highScore': 100,
                'color': "#0f9747"
            },
            {
                'sentiment': 'Passive',
                'lowScore': negative_percentual,
                'highScore': passive_percentual,
                'color': "#fdae19"
            },
            {
                'sentiment': 'Negative',
                'lowScore': 0,
                'highScore': negative_percentual,
                'color': "#ee1f25"
            },
        ]
    }
    return res


def comparative_graphics(client, start_date, end_date, tour_id, country_id, city_id, source_stream):
    for stream_id, stream_name in STREAM_CHOICES:
        if stream_name == source_stream:
            source_stream = stream_id
            break

    if not start_date:
        start_date = date.today() - timedelta(days=31)
    if not end_date:
        end_date = date.today()

    reviews = Review.objects.filter(client=client, date__range=(start_date, end_date))

    if source_stream != 'all':
        reviews = reviews.filter(source_stream=source_stream)

    if tour_id and tour_id != 'all':
        tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
        if tour_ids:
            reviews = reviews.filter(tour_id__in=tour_ids)

    if country_id and country_id != 'all':
        country_ids = [int(id) for id in country_id.strip('[]').split(',')]
        if country_ids:
            reviews = reviews.filter(country_id__in=country_ids)

    if city_id and city_id != 'all':
        reviews = reviews.filter(city_id=city_id)

    reviews = reviews.filter(date__gte=client.date_joined)

    result = (
        reviews
        .values('source_stream', 'product')
        .annotate(
            positive=Count('id', filter=Q(rating=5)),
            passive=Count('id', filter=Q(rating=4)),
            negative=Count('id', filter=Q(rating__lte=3)),
            agency=Case(
                *[When(source_stream=k, then=Value(v['name'])) for k, v in SOURCE_STREAM.items()],
                output_field=CharField()
            ),
            tour=F('product'),

        )
        .order_by('source_stream', 'product')
    )
    return result


def reviews_location(client, start_date, end_date, tour_id, country_id, city_id, source_stream):

    for stream_id, stream_name in STREAM_CHOICES:
        if stream_name == source_stream:
            source_stream = stream_id
            break
    if not start_date:
        start_date = date.today() - timedelta(days=31)
    if not end_date:
        end_date = date.today()

    reviews = Review.objects.filter(client=client, date__range=(start_date, end_date))
    if source_stream != 'all':
        reviews = reviews.filter(source_stream=source_stream)

    if tour_id and tour_id != 'all':
        tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
        if tour_ids:
            reviews = reviews.filter(tour_id__in=tour_ids)

    if country_id and country_id != 'all':
        country_ids = [int(id) for id in country_id.strip('[]').split(',')]
        if country_ids:
            reviews = reviews.filter(country_id__in=country_ids)

    if city_id and city_id != 'all':
        reviews = reviews.filter(city_id=city_id)
    reviews = reviews.annotate(
        country_code_annotation=F('country__code'),
        country_name_annotation=F('country__name')
    ) \
        .values('country_code_annotation', 'country_name_annotation') \
        .annotate(total_reviews=Count('id')) \
        .annotate(
        positive=Count('id', filter=Q(rating=5)),
        passive=Count('id', filter=Q(rating=4)),
        negative=Count('id', filter=Q(rating__lte=3)),
    ) \
        .values('country_code_annotation', 'country_name_annotation', 'total_reviews', 'positive', 'passive',
                'negative')

    reviews = reviews.filter(date__gte=client.date_joined)

    response_data = []
    for review in reviews:
        # if not review['country_code_annotation'] or len(review['country_code_annotation']) < 2:
        #     continue
        color = ''
        positive_totalvalue = max(review.get('positive', 0), review.get('passive', 0), review.get('negative', 0))
        if review.get('positive', 0) == positive_totalvalue:
            color = '#28a745'
        elif review.get('passive', 0) == positive_totalvalue:
            color = '#ffc107'
        elif review.get('negative', 0) == positive_totalvalue:
            color = '#ff4e36'
        review['id'] = review['country_code_annotation']
        review['name'] = review['country_code_annotation']
        review['value'] = review['total_reviews'],
        review['color'] = color

        country_name = review['country_name_annotation']

        if review['negative'] == 0:
            sentiment_percentage = 100
        else:
            sentiment_ratio = review['positive'] / (review['positive'] + review['negative'])
            sentiment_percentage = sentiment_ratio * 100

        response_data.append({
            'id': review['country_code_annotation'],
            'name': country_name,
            'value': review['total_reviews'],
            'positive': review['positive'],
            'passive': review['passive'],
            'negative': review['negative'],
            'sentiment_percentage': round(sentiment_percentage, 2),
            'color': color
        })

    return sorted(response_data, key=lambda d: d['positive'], reverse=True)


def reputation(client, start_date, end_date, tour_id, country_id, city_id, source_stream):
    data = []

    if type(start_date) == datetime:
        start_date = start_date.date()

    if start_date < client.date_joined.date():
        start_date = client.date_joined.date()

    days_diff = date.today() - start_date

    for stream in SOURCE_STREAM:
        stream_reviews = Review.objects.filter(client=client, source_stream=stream, date__range=(start_date, end_date))

        if tour_id and tour_id != 'all':
            tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
            if tour_ids:
                stream_reviews = stream_reviews.filter(tour_id__in=tour_ids)

        if country_id and country_id != 'all':
            country_ids = [int(id) for id in country_id.strip('[]').split(',')]
            if country_ids:
                stream_reviews = stream_reviews.filter(country_id__in=country_ids)

        if city_id and city_id != 'all':
            stream_reviews = stream_reviews.filter(city_id=city_id)

        reviews_count = stream_reviews.count()
        negatives_count = stream_reviews.filter(rating__lte=3).count()
        positive_count = stream_reviews.filter(rating=5).count()
        if negatives_count == 0:
            sentiment_percentage = 0
        else:
            sentiment_ratio = positive_count / (positive_count + negatives_count)
            sentiment_percentage = sentiment_ratio * 100

        stream_reviews_previous = Review.objects.filter(client=client, source_stream=stream,
                                                        date__gte=start_date - days_diff, date__lte=start_date)
        negatives_count_previous = stream_reviews_previous.filter(rating__lte=3).count()
        positive_count_previous = stream_reviews_previous.filter(rating=5).count()
        if negatives_count_previous == 0:
            sentiment_percentage_previous = 0
        else:
            sentiment_ratio = positive_count_previous / (positive_count_previous + negatives_count_previous)
            sentiment_percentage_previous = sentiment_ratio * 100
            sentiment_percentage_previous = sentiment_percentage - sentiment_percentage_previous

        data.append({
            "stream": SOURCE_STREAM[stream]['template_name'],
            "stream_name": SOURCE_STREAM[stream]['name'],
            "reviews": reviews_count,
            "negative": negatives_count,
            "score": round(sentiment_percentage, 2),
            "score_variation": round(sentiment_percentage_previous, 2)
        })
    return data


def keywords(user_word, number_of_repetitions, number_of_repetitions_variation, client, start_date, end_date, tour_id, country_id, city_id, source_stream, number_keywords=5):
    for stream_id, stream_name in STREAM_CHOICES:
        if stream_name == source_stream:
            source_stream = stream_id
            break

    if not start_date:
        start_date = date.today() - timedelta(days=31)
    else:
        start_date = date.fromisoformat(start_date)
    if not end_date:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end_date)

    if type(start_date) == datetime:
        start_date = start_date.date()

    if start_date < client.date_joined.date():
        start_date = client.date_joined.date()

    stop_words = set(stopwords.words('english'))
    stop_words.add('')

    reviews = Review.objects.filter(client=client, date__range=(start_date, end_date)).exclude(places=None)
    if source_stream != 'all':
        reviews = reviews.filter(source_stream=source_stream)

    if tour_id and tour_id != 'all':
        tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
        if tour_ids:
            reviews = reviews.filter(tour_id__in=tour_ids)

    if country_id and country_id != 'all':
        country_ids = [int(id) for id in country_id.strip('[]').split(',')]
        if country_ids:
            reviews = reviews.filter(country_id__in=country_ids)

    if city_id and city_id != 'all':
        reviews = reviews.filter(city_id=city_id)

    # stop_words = set(['that', 'were', 'will', 'with', 'tour', 'guide', 'tour', 'time', "have", "there", "this", 'para', 'pero'])
    wordnet_lemmatizer = WordNetLemmatizer()

    # Get all reviews with positive or negative sentiment
    reviews = reviews.filter(sentiment__in=[Review.POSITIVE, Review.NEGATIVE])
    # Initialize frequency counters for positive and negative reviews
    positive_word_freq = Counter()
    negative_word_freq = Counter()

    # Loop over reviews and count word frequencies for positive and negative sentiment
    for review in reviews:
        words = preprocess_text(review.places, stop_words, wordnet_lemmatizer)
        if review.sentiment == Review.POSITIVE:
            positive_word_freq.update(words)
        elif review.sentiment == Review.NEGATIVE:
            negative_word_freq.update(words)

    # Get the top 5 most frequent words for positive and negative sentiment
    top_positive_words = positive_word_freq.most_common(number_keywords)
    top_negative_words = negative_word_freq.most_common(number_keywords)

    # Initialize a list to store the results
    results_positive = []
    results_negative = []

    # Loop over the top positive words and compute the statistics
    for word, count in top_positive_words:
        # Compute the variation in the number of repetitions and impact
        positive_variation = (positive_word_freq[word] - negative_word_freq[word]) / (
                positive_word_freq[word] + negative_word_freq[word])
        impact = positive_word_freq[word] - negative_word_freq[word]
    

        # Append the result to the list
        results_positive.append({
            'word': word,
            'number_of_repetitions': positive_word_freq[word],
            'number_of_repetitions_variation': round(positive_variation, 2),
            'impact': round(impact, 2),
            'impact_variation': None
        })

    # Loop over the top negative words and compute the statistics
    for word, count in top_negative_words:
        # Compute the variation in the number of repetitions and impact
        positive_variation = (negative_word_freq[word] - positive_word_freq[word]) / (
                negative_word_freq[word] + positive_word_freq[word])
        impact = negative_word_freq[word] - positive_word_freq[word]


        # Append the result to the list
        results_negative.append({
            'word': word,
            'number_of_repetitions': negative_word_freq[word],
            'number_of_repetitions_variation': round(positive_variation, 2),
            'impact': round(impact, 2),
            'impact_variation': None
        })


    #Filter results of positive and negative
    positive_filtered_results = []
    negative_filtered_results = []

    for result in results_positive:
        word = result['word']
        repetitions = result['number_of_repetitions']
        repetitions_variation = result['number_of_repetitions_variation']

        # Check different combinations of provided parameters
        if not user_word and not number_of_repetitions and not number_of_repetitions_variation:
            positive_filtered_results.append(result)
        else:
            if ((not str(user_word).lower() or str(user_word).lower() in str(word).lower()) and
            (not number_of_repetitions or repetitions == number_of_repetitions) and
            (not number_of_repetitions_variation or round(repetitions_variation, 2) == number_of_repetitions_variation)):
                positive_filtered_results.append(result)
    
    for result in results_negative:
        word = result['word']
        repetitions = result['number_of_repetitions']
        repetitions_variation = result['number_of_repetitions_variation']

        # Check different combinations of provided parameters
        if not user_word and not number_of_repetitions and not number_of_repetitions_variation:
            negative_filtered_results.append(result)
        else:
           if ((not str(user_word).lower() or str(user_word).lower() in str(word).lower()) and
            (not number_of_repetitions or repetitions == number_of_repetitions) and
            (not number_of_repetitions_variation or round(repetitions_variation, 2) == number_of_repetitions_variation)):
                negative_filtered_results.append(result)


    return {
        'positive': positive_filtered_results,
        'negative': negative_filtered_results,
    }

def trending_keywords(user_word, number_of_repetitions, number_of_repetitions_variation, client, start_date, end_date, tour_id, country_id, city_id, source_stream, number_keywords=5):
    for stream_id, stream_name in STREAM_CHOICES:
        if stream_name == source_stream:
            source_stream = stream_id
            break

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

    if not start_date:
        start_date = date.today() - timedelta(days=31)
    if not end_date:
        end_date = date.today()

    if type(start_date) == datetime:
        start_date = start_date.date()

    if start_date < client.date_joined.date():
        start_date = client.date_joined.date()

    stop_words = set(stopwords.words('english'))
    stop_words.add('')

    reviews = Review.objects.filter(client=client, date__range=(start_date, end_date)).exclude(places=None)
    if source_stream != 'all':
        reviews = reviews.filter(source_stream=source_stream)

    if tour_id and tour_id != 'all':
        reviews = reviews.filter(tour_id=tour_id)

    if country_id and country_id != 'all':
        reviews = reviews.filter(country_id=country_id)

    if city_id and city_id != 'all':
        reviews = reviews.filter(city_id=city_id)

    # stop_words = set(['that', 'were', 'will', 'with', 'tour', 'guide', 'tour', 'time', "have", "there", "this", 'para', 'pero'])
    wordnet_lemmatizer = WordNetLemmatizer()

    # Get all reviews with positive or negative sentiment
    reviews = reviews.filter(sentiment__in=[Review.POSITIVE, Review.NEGATIVE])
    # Initialize frequency counters for positive and negative reviews
    positive_word_freq = Counter()
    negative_word_freq = Counter()

    # Loop over reviews and count word frequencies for positive and negative sentiment
    for review in reviews:
        words = preprocess_text(review.places, stop_words, wordnet_lemmatizer)
        if review.sentiment == Review.POSITIVE:
            positive_word_freq.update(words)
        elif review.sentiment == Review.NEGATIVE:
            negative_word_freq.update(words)

    # Get the top 5 most frequent words for positive and negative sentiment
    top_positive_words = positive_word_freq.most_common(number_keywords)
    top_negative_words = negative_word_freq.most_common(number_keywords)

    # Initialize a list to store the results
    results_positive = []
    results_negative = []

    # Loop over the top positive words and compute the statistics
    for word, count in top_positive_words:
             
        # Append the result to the list
        results_positive.append(word)

    # Loop over the top negative words and compute the statistics
    for word, count in top_negative_words:
       
        # Append the result to the list
        results_negative.append(word)

    keywords = results_positive + results_negative

    return {
        'keyword':keywords,
    }


def preprocess_text(places, stop_words, wordnet_lemmatizer):
    # Convert text to lowercase
    # text = text.lower()
    #
    # # Remove punctuation
    # text = text.translate(str.maketrans('', '', string.punctuation))
    #
    # # Tokenize text into words
    # words = text.split()
    #

    places = json.loads(places)
    # # Remove stopwords
    words = [word['name'] for word in places if word['name'] not in stop_words and word['type'] == 'restaurant']
    # # Lemmatize words
    words = [wordnet_lemmatizer.lemmatize(word) for word in words]
    return words