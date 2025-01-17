from langchain.agents import Tool
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
import pandas as pd

def setup_knowledge_base(product_catalog: str = None):
    """
    We assume that the product catalog is simply a text string.
    """
    # load product catalog
    df = pd.read_csv(product_catalog)

    # Convert each row of the dataframe to a separate string and store them in a list
    texts = df.apply(lambda row: ' '.join(row.astype(str)), axis=1).tolist()
    
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=500,
        length_function=len
    )
    chunks = text_splitter.split_text(texts)
    
    llm = OpenAI(temperature=0)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(
         chunks, embeddings, collection_name="product-knowledge-base"
    )

    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=docsearch.as_retriever()
    )
    return knowledge_base


def get_tools(knowledge_base):
    # we only use one tool for now, but this is highly extensible!
    tools = [
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            description="useful for when you need to answer questions about product information",
        )
    ]

    return tools
