"""Recreate database, graph corpus, graph questions, documents, and verification."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ('build_database.py','build_visual_data.py','build_graph_questions.py','build_documents.py','validate_database.py','visual_contract.py'):
    subprocess.run([sys.executable,str(root/script)],check=True)
