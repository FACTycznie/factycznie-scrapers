class InvalidArticleError(Exception):
    """Raised when a webpage is not an article"""

# Minimum length of the body of an article in characters
MINIMUM_ARTICLE_LENGTH = 400

# Maximum length of characters that the last line can be for us to
# still consider it a signature line
MAXIMUM_AUTHOR_LINE_LENGTH = 50
