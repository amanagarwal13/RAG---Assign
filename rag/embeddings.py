import os
import logging
from typing import List, Dict, Any, Union
import numpy as np

# LangChain imports
from langchain_openai  import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings

logger = logging.getLogger(__name__)

class OpenAILangChainEmbeddings:
    """
    Unified wrapper around LangChain's OpenAIEmbeddings.
    """
    def __init__(self, api_key: str = None, model_name: str = "text-embedding-3-large"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        self.model = OpenAIEmbeddings(openai_api_key=self.api_key, model=model_name)

    def generate(self, texts: Union[List[str], str]) -> np.ndarray:
        """
        Embed a single string or list of strings.
        Returns an (n, dim) array or a (dim,) vector if single.
        """
        single = False
        if isinstance(texts, str):
            texts = [texts]
            single = True
        try:
            emb = self.model.embed_documents(texts)
            arr = np.array(emb)
            return arr[0] if single else arr
        except Exception as e:
            logger.error("Error generating embeddings", exc_info=True)
            raise

    def get_dimension(self) -> int:
        """
        Return the dimensionality of the embeddings.
        """
        # attribute name depends on LangChain version
        return getattr(self.model, "embedding_dim", None) or self.model.model_kwargs.get("embedding_dim")