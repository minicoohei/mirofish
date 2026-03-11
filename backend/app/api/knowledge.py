"""
Knowledge Curation API routes
Trigger knowledge curation and check status
"""

from flask import request, jsonify

from . import knowledge_bp
from ..services.knowledge_curator import KnowledgeCurator
from ..services.knowledge_loader import KnowledgeLoader
from ..services.zep_entity_reader import ZepEntityReader
from ..utils.logger import get_logger

logger = get_logger('mirofish.api.knowledge')


@knowledge_bp.route('/curate', methods=['POST'])
def trigger_curation():
    """Trigger knowledge curation for a graph

    Request body:
        graph_id: str - Zep graph ID
        candidate_context: str - Optional candidate document text
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    graph_id = data.get("graph_id")
    candidate_context = data.get("candidate_context", "")

    if not graph_id:
        return jsonify({"error": "graph_id is required"}), 400

    try:
        # Read ontology entities from Zep graph
        entity_reader = ZepEntityReader()
        filtered = entity_reader.filter_defined_entities(graph_id)
        ontology_entities = [
            {
                "name": node.name,
                "type": node.labels[0] if node.labels else "Unknown",
                "summary": node.summary or ""
            }
            for node in (filtered.entities if filtered else [])
        ]

        # Run curation
        curator = KnowledgeCurator()
        result = curator.curate_for_ontology(
            ontology_entities=ontology_entities,
            candidate_context=candidate_context,
            graph_id=graph_id
        )

        return jsonify({
            "status": "success",
            "classification": result["classification"],
            "files_count": result["stats"]["files"],
            "curated_files": [str(f) for f in result["curated_files"]],
            "stats": result["stats"]
        })

    except Exception as e:
        logger.exception(f"Knowledge curation failed: {e}")
        return jsonify({"error": "Knowledge curation failed. Please try again later."}), 500


@knowledge_bp.route('/status', methods=['GET'])
def knowledge_status():
    """Check status of curated knowledge files"""
    status = KnowledgeLoader.get_status()
    return jsonify(status)


@knowledge_bp.route('/search', methods=['POST'])
def search_knowledge():
    """Search knowledge base

    Request body:
        query: str - Search query
        category: str - Category filter (optional, default "all")
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    query = data.get("query", "")
    category = data.get("category", "all")

    if not query:
        return jsonify({"error": "query is required"}), 400

    result = KnowledgeLoader.search_knowledge(query=query, category=category)
    return jsonify({"query": query, "category": category, "result": result})
