import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

load_dotenv() 
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
def get_vectorstore(pdf_path: str, db_dir: str, embeddings):
    if os.path.exists(db_dir):
        return Chroma(persist_directory=db_dir, embedding_function=embeddings)

    loader = PyMuPDFLoader(pdf_path)
    chunks = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=250).split_documents(loader.load())
    return Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=db_dir)

def run_marketing_agent():
    db_dir = "./chroma_db_marketing"
    pdf_path = "markting book.pdf"

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = get_vectorstore(pdf_path, db_dir, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

    @tool
    def marketing_book_retriever(query: str) -> str:
        """Searches and returns excerpts from the Marketing book to answer marketing strategy, campaigns, or customer segment questions."""
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])

    tools = [marketing_book_retriever]

    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        model="qwen/qwen-2.5-72b-instruct",
        temperature=0.0,
        max_tokens=2048
    )
    
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = """
    You are an elite AI Marketing Campaign Strategist.
    Respond in the same language as the user's query.

    Query Classification & Rules:
    1. Greetings/Conversational: Respond naturally and politely. DO NOT use the retrieval tool.
    2. OOD & Safety Guardrails: If asked for medical, diagnostic, financial advice, or topics outside marketing, refuse immediately. DO NOT use the retrieval tool.
    3. In-Domain (Marketing): You MUST use the 'marketing_book_retriever' tool to fetch context before answering.
    
    When answering using the retrieved context, format your output EXACTLY as follows:
    ### درجة الموثوقية
    [High / Medium / Low]

    ### الإجابة والتحليل
    [Direct answer and analysis based ONLY on the retrieved text]
    """

    print("\n Type your question (or 'exit' to quit).\n")
    
    while True:
        try:
            user_input = input("User: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]

            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            if ai_msg.tool_calls:
                for tool_call in ai_msg.tool_calls:
                    tool_query = tool_call["args"].get("query", user_input)
                    tool_output = marketing_book_retriever.invoke(tool_query)
                    
                    messages.append(ToolMessage(
                        tool_call_id=tool_call["id"], 
                        name=tool_call["name"], 
                        content=tool_output
                    ))
                
                final_ai_msg = llm_with_tools.invoke(messages)
                print("\nAgent:\n" + final_ai_msg.content)
                
            else:
                print("\nAgent:\n" + ai_msg.content)
            
            print("\n" + "=" * 60 + "\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nSystem Error: {str(e)}")

if __name__ == "__main__":
    run_marketing_agent()
