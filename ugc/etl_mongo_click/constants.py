from models import (
    Review,
    Bookmark,
    ReviewRating
)

ASSOCIATION_COLLECTION_TO_SCHEMA = {
    'review': Review,
    'bookmark': Bookmark,
    'review_rating': ReviewRating
}

ASSOCIATION_COLLECTION_TO_CH_TABLE = {
    'review': 'reviews',
    'bookmark': 'bookmarks',
    'review_rating': 'review_ratings'
}
