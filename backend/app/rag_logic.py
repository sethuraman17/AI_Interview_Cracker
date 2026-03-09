import os
import pickle
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# =========================
# ENV
# =========================
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text

# =========================
# LOAD VECTORSTORE
# =========================
with open("app/vectorstore/resume_faiss.pkl", "rb") as f:
    vectorstore_index = pickle.load(f)

retriver = vectorstore_index.as_retriever()

# =========================
# LLM
# =========================
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1
)

# =========================
# PROMPTS (UNCHANGED)
# =========================
classification_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are a classifier. Categorize the following question into one of two categories:
1. resume_specific
2. general_ai_ml

Question: {question}

Return ONLY the category name.
"""
)

resume_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Answer the question based ONLY on the following context.
If the answer is not present in the context, say "I don't know."

Context:
{context}

Question:
{question}
"""
)

general_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are an AI/ML interview assistant.

Answer the following question clearly and concisely.
If you don't know the answer, say so.

Question:
{question}
"""
)

# =========================
# CORE FUNCTION (UNCHANGED)
# =========================
def conditional_rag_answer(user_question: str) -> str:
    classification_chain = classification_prompt | llm
    classification_response = classification_chain.invoke(
        {"question": user_question}
    )
    category = classification_response.content.strip()

    if category == "resume_specific":
        docs = retriver.invoke(user_question)
        context = "\n\n".join([doc.page_content for doc in docs])
        response = (resume_prompt | llm).invoke(
            {"context": context, "question": user_question}
        )
        return response.content

    else:
        response = (general_prompt | llm).invoke(
            {"question": user_question}
        )
        return response.content

