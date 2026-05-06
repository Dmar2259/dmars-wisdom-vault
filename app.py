import streamlit as st
from google import genai
import chromadb
from chromadb.utils import embedding_functions

# --- 1. CONFIGURATION ---
# Replace with your actual key if it's not already there
client = genai.Client(api_key="AIzaSyDtE-R9RT72nvDtCi8VAyPyviVaR9DbNAM")
# Connect to the database
client = chromadb.PersistentClient(path="./wisdom_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="wisdom_vault", embedding_function=sentence_transformer_ef)

st.set_page_config(page_title="Dmar's Wisdom Vault", layout="wide")
st.title("🧠 Dmar's Wisdom Vault")

# --- 2. SIDEBAR (The Input and The History) ---
with st.sidebar:
    st.header("📥 Feed the Vault")
    category = st.selectbox("Category", ["Psychology", "Philosophy", "Ideas", "Health", "Exercise", "Relationships", "Computers", "Cars", "Banking&Investments", "Socializing", "Chatuplines",])
    new_insight = st.text_area("What did you observe today?")

# New field for the source
    source_info = st.text_input("Source (YouTube, Instagram, Website, Person, Jack, Book name)", placeholder="Optional")    
    if st.button("Save Insight"):
        if new_insight:
            formatted_entry = f"[{category}] {new_insight}"
            count = collection.count()
            collection.add(documents=[formatted_entry], ids=[f"id_{count}"])
            st.success("Insight Vaulted!")
            st.rerun() # Rerun so the list updates immediately

    st.divider()
    st.subheader("📜 Recent Activity")
    
    # Fetch all data
    all_data = collection.get()
    
    if all_data['documents']:
        # [::-1] reverses the list so newest is first
        # [:5] takes only the first 5 items from that reversed list
        recent_five = all_data['documents'][::-1][:5]
        
        for doc in recent_five:
            # Use small text for a cleaner look
            st.caption(doc)
    else:
        st.write("No insights yet.")

# --- 3. MAIN AREA (The Brain) ---
user_query = st.text_input("Ask the Vault a question:")

if user_query:
    # 1. Search the local DB for relevant notes
    results = collection.query(query_texts=[user_query], n_results=3)
    context = "\n".join(results['documents'][0])
    
    # 2. Use the verified 'gemini-flash-latest' brain
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    try:
        response = client.models.generate_content(
            model="models/gemini-1.5-flash"
            contents=f"You are Jack's Personal Wisdom Assistant. Use these notes: {context}. "
                     f"Answer the question: '{user_query}' as concisely as possible. "
                     f"If the answer isn't in the notes, say 'I don't have that in the vault yet, Jack.'"
        )
        st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")




