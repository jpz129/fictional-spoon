import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import json
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import AIMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

from pathlib import Path
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain.prompts import PromptTemplate
from langchain.schema import Document
from backend.app.models import ContractTasks

# Directory containing raw contract DOCX files
DATA_DIR = Path(__file__).parent / "contracts_raw"

# Initialize LLM and prompt
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
prompt = PromptTemplate(
    input_variables=["contract"],
    template=(
        "You are a government contracting assistant.\n"
        "Your task is to extract every distinct obligation or action item assigned to the contractor "
        "from the following contract text. Return a JSON array of strings.\n"
        "Each string should describe one clearly defined task or responsibility.\n"
        "Avoid general summaries—focus on task-level granularity. Do not include government tasks.\n\n"
        "{contract}"
    )
)
chain = prompt | llm

# Collect task documents
task_docs = []
for docx_path in DATA_DIR.glob("*.docx"):
    loader = UnstructuredWordDocumentLoader(str(docx_path))
    docs = loader.load()
    full_text = " ".join([d.page_content for d in docs])
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=300,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(full_text)
    print("\n" + "="*40)
    print(f"📄 Contract: {docx_path.name}")
    print("="*40)
    print(f"🔹 Sections loaded: {len(docs)}")
    print(f"🔹 Split into {len(chunks)} chunk(s) for LLM processing")

    all_tasks = []
    for i, chunk in enumerate(chunks, 1):
        print(f"  🧠 Processing chunk {i}/{len(chunks)}...")
        response = chain.invoke({"contract": chunk})
        print(f"    ↳ Type: {type(response)}")

        if isinstance(response, dict) and "text" in response:
            tasks_json = response["text"]
        elif isinstance(response, AIMessage):
            tasks_json = response.content
        elif isinstance(response, str):
            tasks_json = response
        else:
            raise TypeError(f"Unexpected response type from LLM chain: {type(response)}")

        print(f"    ↳ Raw: {tasks_json[:100]}..." if len(tasks_json) > 100 else f"    ↳ Raw: {tasks_json}")
        try:
            tasks = json.loads(tasks_json)
            print(f"    ↳ Parsed {len(tasks)} task(s)")
            all_tasks.extend(tasks)
        except json.JSONDecodeError:
            print("    ⚠️ Failed to parse JSON. Skipping this chunk.")

    print(f"🔹 Combined extracted tasks: {len(all_tasks)}")
    contract_tasks = ContractTasks(
        contract_id=docx_path.stem,
        contract_text="",
        tasks=all_tasks
    )
    for i, task in enumerate(all_tasks, 1):
        print(f"  {i}. {task}")
        task_docs.append(
            Document(
                page_content=task,
                metadata={
                    "contract_id": contract_tasks.contract_id
                }
            )
        )

print("\n✅ Finished processing all contracts.")
print(f"📦 Total tasks indexed: {len(task_docs)}")
print("💾 Building FAISS index with OpenAI embeddings...")
# Build embeddings and vectorstore
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
vectorstore = FAISS.from_documents(task_docs, embeddings)

# Save the vectorstore
output_dir = Path(__file__).parents[1] / "backend" / "app" / "faiss"
vectorstore.save_local(str(output_dir))
print(f"Saved vectorstore to: {output_dir}")