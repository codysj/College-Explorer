from __future__ import annotations

import argparse
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from db.session import SessionLocal
from repositories.schools import SchoolRepository
from services.semantic_search import EMBEDDING_TYPE, SemanticSearchService


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or refresh V2.2 school search embeddings.")
    parser.add_argument("--dry-run", action="store_true", help="Build documents without writing embeddings.")
    args = parser.parse_args()

    with SessionLocal() as db:
        repository = SchoolRepository(db)
        if args.dry_run:
            documents = repository.get_semantic_document_rows()
            print(f"Prepared {len(documents)} {EMBEDDING_TYPE} source documents")
            return

        service = SemanticSearchService(repository)
        refreshed = service.refresh_embeddings()
        db.commit()
        print(f"Refreshed {refreshed} {EMBEDDING_TYPE} embeddings with {service.embedding_provider.model}")


if __name__ == "__main__":
    main()
