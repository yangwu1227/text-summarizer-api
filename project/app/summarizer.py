import nltk
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.utils import get_stop_words

from app.models.pydantic import SummarizationMethod
from app.models.tortoise import TextSummary

LANGUAGE = "english"
stop_words = get_stop_words(LANGUAGE)

summarizers = {
    "lsa": LsaSummarizer,
    "lex_rank": LexRankSummarizer,
    "text_rank": TextRankSummarizer,
    "edmundson": EdmundsonSummarizer,
}


async def generate_summary(
    id: int, url: str, summarization_method: SummarizationMethod, sentence_count: int
) -> None:
    """
    Create a summary of an article from a given URL using the `sumy` package. The summarization methods available include:

    - **Edmundson**: Enhanced Luhn method with pragmatic words and positional heuristics.
    - **LSA (Latent Semantic Analysis)**: Algebraic, language-independent, identifies synonyms.
    - **LexRank/TextRank**: Graph-based, finds connections between sentences.

    Parameters
    ----------
    id: int
        The generated id for this summary record.
    url : str
        The URL of the article to summarize.
    summarization_method : SummarizationMethod
        The summarization algorithm to use.
    sentence_count : int
        The number of sentences in the summary.

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
        # Note that this is an enum instance
        summarizer_name = summarization_method.value
        # Parse content from the provided URL
        parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))

        # Apply stemmer and stop words processing
        stemmer = Stemmer(LANGUAGE)
        summarizer = summarizers[summarizer_name](stemmer)
        if summarizer_name == "edmundson":
            summarizer.bonus_words = parser.significant_words
            summarizer.stigma_words = parser.stigma_words
            summarizer.null_words = stop_words
        elif summarizer_name in ["lsa", "lex_rank", "text_rank"]:
            summarizer.stop_words = stop_words

        # Generate the summary
        summary = "\n".join(
            sentence._text for sentence in summarizer(parser.document, sentence_count)
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
