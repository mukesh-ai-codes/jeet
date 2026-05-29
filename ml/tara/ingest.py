#!/usr/bin/env python3
"""Tara RAG — ingest NCERT corpus into ChromaDB."""
import json
import chromadb
CORPUS = "ml/tara/ncert_corpus.json"
CHROMA_DIR = "ml/tara/chroma_db"
def main():
    docs = json.load(open(CORPUS))
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try: client.delete_collection("ncert")
    except Exception: pass
    col = client.create_collection("ncert")
    col.add(
        ids=[d["id"] for d in docs],
        documents=[f"{d['chapter']} ({d['subject']}). {d['content']} Analogy: {d['analogy']}" for d in docs],
        metadatas=[{"subject":d["subject"],"chapter":d["chapter"],"exam":d["exam"]} for d in docs])
    print(f"Ingested {col.count()} chapters into {CHROMA_DIR}")
if __name__ == "__main__":
    main()
