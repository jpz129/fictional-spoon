from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# LLM and prompt imports for explanation generation
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# Directory where the FAISS vectorstore was saved by preprocessing
VECTORSTORE_DIR = Path(__file__).parent / "faiss"

# Initialize OpenAI embeddings model (must match preprocessing)
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Load the FAISS vectorstore
vectorstore = FAISS.load_local(str(VECTORSTORE_DIR), embeddings, allow_dangerous_deserialization=True)

# Initialize LLM and explanation chain for explanations
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
explanation_prompt = PromptTemplate(
    input_variables=["query", "tasks", "previous_explanation"],
    template=(
        "The user originally searched for:\n\"{query}\"\n\n"
        "Here are tasks from a similar contract:\n{tasks}\n\n"
        "Previously, you explained:\n\"{previous_explanation}\"\n\n"
        "Now, write a new explanation in 1-2 sentences that logically continues from the previous explanation, "
        "highlighting how this new contract's tasks are still semantically related to the query."
    )
)
explanation_chain = explanation_prompt | llm

summary_prompt = PromptTemplate(
    input_variables=["query", "tasks", "previous_explanation"],
    template=(
        "The user searched for:\n\"{query}\"\n\n"
        "Here are all tasks retrieved from the most similar contracts:\n{tasks}\n\n"
        "The final previous explanation was:\n\"{previous_explanation}\"\n\n"
        "Write a final summary that explains why these tasks are semantically related to the query. "
        "Also suggest if these contracts could be consolidated based on thematic or functional overlap."
    )
)
summary_chain = summary_prompt | llm

def search_tasks(query: str, k: int = 5):
    print("\n🔍 Starting vectorstore search...")
    print(f"  Query: {query}")
    print(f"  Top {k*k} documents retrieved before grouping.\n")

    docs_and_scores = vectorstore.similarity_search_with_score(query, k=k*k)
    grouped = {}

    for doc, score in docs_and_scores:
        cid = doc.metadata.get("contract_id", "unknown")
        print(f"    🧩 Found task: '{doc.page_content[:80]}...' from contract '{cid}' with similarity {score:.4f}")
        if cid not in grouped:
            grouped[cid] = {
                "contract_id": cid,
                "similarity": score,
                "tasks": set(),
            }
        grouped[cid]["similarity"] = min(grouped[cid]["similarity"], score)
        grouped[cid]["tasks"].add(doc.page_content)

    print(f"\n📦 Grouped into {len(grouped)} contracts.\n")

    top_contracts = sorted(grouped.values(), key=lambda x: x["similarity"])[:k]

    print("🏆 Top similar contracts selected:")
    for c in top_contracts:
        print(f"   - {c['contract_id']} (best similarity: {c['similarity']:.4f})")
    print("\n✅ Search processing complete.\n")

    results = []
    previous_explanation = ""
    all_explanations = []
    for c in top_contracts:
        task_list = list(c["tasks"])
        explanation_response = explanation_chain.invoke({
            "query": query,
            "tasks": "\n".join(task_list[:5]),
            "previous_explanation": previous_explanation
        }).content
        previous_explanation = explanation_response
        all_explanations.append(explanation_response)
        results.append({
            "contract_id": c["contract_id"],
            "similarity": c["similarity"],
            "tasks": task_list,
            "explanation": explanation_response
        })
    joined_tasks = "\n".join(task for contract in results for task in contract["tasks"])
    joined_explanations = "\n".join(all_explanations)
    final_summary = summarize_group(query, joined_tasks, joined_explanations)
    print("\n🧾 FINAL SUMMARY GENERATED:")
    print("────────────────────────────")
    print(final_summary)
    print("────────────────────────────\n")
    return {
        "contracts": results,
        "final_summary": final_summary
    }

def summarize_group(query: str, tasks: str, previous_explanation: str) -> str:
    response = summary_chain.invoke({
        "query": query,
        "tasks": tasks,
        "previous_explanation": previous_explanation
    }).content
    return response