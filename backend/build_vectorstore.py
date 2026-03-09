import pickle
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

# ===== PATH TO YOUR RESUME =====
RESUME_PATH = "data/resume.pdf"

# ===== EXTRACT TEXT =====
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text

resume_text = extract_text_from_pdf(RESUME_PATH)

# ===== SPLIT TEXT =====
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " ", ""]
)

chunks = text_splitter.split_text(resume_text)
documents = [Document(page_content=chunk) for chunk in chunks]

# ===== EMBEDDINGS =====
embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# ===== FAISS =====
vectorstore = FAISS.from_documents(documents, embeddings)

# ===== SAVE =====
with open("app/vectorstore/resume_faiss.pkl", "wb") as f:
    pickle.dump(vectorstore, f)

print("Vectorstore built successfully.")
