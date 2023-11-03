import facebook
from api.models import Review, FACEBOOK, INSTAGRAM
from .utils import clean_review, clean_date
from django.conf import settings


def get_facebook_comments(obj):
    client = obj.user.created_by if obj.user.created_by else obj.user

    graph = facebook.GraphAPI(obj.api_key)
    comments = []
    fields = 'id,message,created_time,comments.limit(10),permalink_url'

    posts = graph.get_connections(obj.page_id, 'posts', fields=fields)

    for p in posts['data']:
        if 'comments' in p:
            for c in p['comments']['data']:
                try:
                    Review.objects.get_or_create(
                        date=clean_date(c['created_time']),
                        product_id=c['id'],
                        defaults={
                            "rating": 0,
                            "review_text": clean_review(c['message']),
                            "responded": False,
                            "source_stream": FACEBOOK,
                            "review_url": p['permalink_url'],
                            "can_respond": True,
                            "client": client,
                            "review_got_from": obj.page_id
                        })
                except:
                    pass

    return comments


def get_facebook_reviews(obj):
    client = obj.user.created_by if obj.user.created_by else obj.user

    try:
        graph = facebook.GraphAPI(obj.api_key)

        # Campi da recuperare insieme alle recensioni, incluso il testo della recensione e la relativa valutazione numerica
        fields = 'rating,reviewer,has_rating,review_text,recommendation_type,created_time,has_review,open_graph_story'
        reviews = graph.get_connections(obj.page_id, 'ratings', fields=fields)

        for r in reviews['data']:
            try:
                user_id = r['open_graph_story']['id']
                review_text = r['review_text'] if r['has_review'] else ''
                date = r['created_time']
                rating = r['rating'] if r['has_rating'] else 0
                Review.objects.get_or_create(
                    date=clean_date(date),
                    product_id=f"{date}_{user_id}",
                    defaults={
                        "rating": rating,
                        "review_text": clean_review(review_text),
                        "responded": False,
                        "source_stream": FACEBOOK,
                        "can_respond": False,
                        "review_url": r['open_graph_story']['data']['seller']['url'],
                        "client": client,  # the User is used here
                        "review_got_from": obj.page_id
                    })
            except:
                pass

        return {
            'data': reviews['data'],
            'success': True
        }

    except Exception as e:
        return {
            'data': [],
            'success': False
        }


def get_instagram_comments(obj):
    client = obj.user.created_by if obj.user.created_by else obj.user

    try:
        comments = []

        graph = facebook.GraphAPI(obj.api_key)
        fields = 'id,comments.limit(10){id,text,replies,timestamp},permalink'
        posts = graph.get_connections(obj.page_id, 'media', fields=fields)

        for p in posts['data']:
            if 'comments' in p:
                for c in p['comments']['data']:
                    try:
                        Review.objects.get_or_create(
                            date=clean_date(c['timestamp']),
                            product_id=c['id'],
                            defaults={
                                "rating": 0,
                                "review_text": clean_review(c['text']),
                                "responded": True if 'replies' in c else False,
                                "source_stream": INSTAGRAM,
                                "review_url": p['permalink'],
                                "can_respond": True,
                                "client": client,  # the User is used here
                                "review_got_from": obj.page_id
                            })
                    except:
                        pass

        return {
            'data': comments,
            'success': True
        }

    except Exception as e:
        return {
            'data': [],
            'success': False
        }


def reply_facebook_comment(review, message, token):
    graph = facebook.GraphAPI(token)
    graph.put_object(parent_object=review.product_id, connection_name='comments', message=message)
    review.responded = True
    review.save()


def reply_instagram_comment(review, message, token):
    graph = facebook.GraphAPI(token)
    graph.put_object(parent_object=review.product_id, connection_name='replies', message=message)
    review.responded = True
    review.save()

