import nltk
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.utils import get_stop_words

from app.models.tortoise import TextSummary

LANGUAGE = "english"
SUMMARY_SENTENCE_COUNT = 10


async def generate_summary(id: int, url: str) -> None:
    """
    Create a summary of an article from a given URL using the `sumy` package. The summarization methods available include:

    - **Random**: A baseline for comparison, not used in real-world applications.
    - **Luhn**: Heuristic, based on significant words (non-stop-words with high frequency).
    - **Edmundson**: Enhanced Luhn method with pragmatic words and positional heuristics.
    - **LSA (Latent Semantic Analysis)**: Algebraic, language-independent, identifies synonyms.
    - **LexRank/TextRank**: Graph-based, finds connections between sentences.
    - **SumBasic**: Baseline, compares against other algorithms.
    - **KL-Sum**: Greedy, reduces KL Divergence between sentences and the document.
    - **Reduction**: Graph-based, computes sentence salience through edge weights.

    Parameters
    ----------
    id: int
        The generated id for this summary record.
    url : str
        The URL of the article to summarize.

    Returns
    -------
    None
    """
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
        nltk.download("punkt_tab")

    try:
        # Parse content from the provided URL
        parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))

        # Apply stemmer and stop words processing
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)

        # Generate the summary
        summary = "\n".join(
            sentence._text for sentence in summarizer(parser.document, SUMMARY_SENTENCE_COUNT)
        )

        # Check if the summary is empty and update with a message if necessary
        if not summary.strip():
            summary = (
                "Summary generation failed resulting in an empty summary; please try another URL"
            )

    except Exception as error:
        # In case of any error, update with a failure message
        summary = f"Summary generation failed due to an error: {str(error)}; please try another URL"

    # Update the summary record in the database
    await TextSummary.filter(id=id).update(summary=summary)
