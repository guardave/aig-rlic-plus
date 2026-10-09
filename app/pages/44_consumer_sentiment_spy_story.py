"""Pair 40 -- U. Michigan Consumer Sentiment x SPY STORY (thin wrapper, APP-PT1)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.page_templates import render_story_page
from pair_configs.consumer_sentiment_spy_config import STORY_CONFIG

render_story_page("consumer_sentiment_spy", STORY_CONFIG)
