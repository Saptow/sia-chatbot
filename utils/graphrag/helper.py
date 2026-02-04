from neo4j_graphrag.retrievers.base import RetrieverResultItem

from typing import Any, Dict, List
try:
    # Neo4j Python driver v5 types (optional import guard)
    from neo4j.graph import Node, Relationship, Path
except Exception:
    Node = Relationship = Path = ()  # fallback for isinstance checks

def _format_props(props: Dict[str, Any]) -> List[str]:
    lines = []
    for k, v in props.items():
        lines.append(f"- {k}: {v}")
    return lines

def generic_result_formatter(record) -> "RetrieverResultItem":
    """
    Pretty-print any Neo4j record:
    - Renders Nodes (labels, element_id, properties)
    - Renders Relationships (type, endpoints, properties)
    - Renders Paths (summary then nodes/rels)
    - Handles lists/dicts/primitives
    Returns RetrieverResultItem(content, metadata) with JSON-safe metadata.
    """
    content_lines: List[str] = []
    metadata: Dict[str, Any] = {}

    for key in record.keys():
        value = record.get(key)

        # --- Node ---
        if isinstance(value, Node) or hasattr(value, "labels"):
            labels = sorted(list(getattr(value, "labels", [])))
            content_lines.append(f"### Node `:{':'.join(labels)}`")
            content_lines.append(f"- element_id: {getattr(value, 'element_id', None)}")
            content_lines += _format_props(dict(value))
            metadata[key] = {
                "type": "node",
                "labels": labels,
                "element_id": getattr(value, "element_id", None),
                "properties": dict(value),
            }

        # --- Relationship ---
        elif isinstance(value, Relationship) or hasattr(value, "type"):
            rel_type = getattr(value, "type", None)
            content_lines.append(f"### Relationship `:{rel_type}`")
            # start/end ids are super useful
            start_eid = getattr(value, "start_node_element_id", None)
            end_eid   = getattr(value, "end_node_element_id", None)
            if start_eid is not None:
                content_lines.append(f"- start_node_element_id: {start_eid}")
            if end_eid is not None:
                content_lines.append(f"- end_node_element_id: {end_eid}")
            content_lines += _format_props(dict(value))
            metadata[key] = {
                "type": "relationship",
                "rel_type": rel_type,
                "start_node_element_id": start_eid,
                "end_node_element_id": end_eid,
                "properties": dict(value),
            }

        # --- Path ---
        elif isinstance(value, Path) or (hasattr(value, "nodes") and hasattr(value, "relationships")):
            content_lines.append(f"### Path")
            content_lines.append(f"- length: {len(value.relationships)}")
            # Brief summary (avoid dumping full objects)
            try:
                node_ids = [getattr(n, "element_id", None) for n in value.nodes]
                rel_types = [getattr(r, "type", None) for r in value.relationships]
                content_lines.append(f"- node_element_ids: {node_ids}")
                content_lines.append(f"- relationship_types: {rel_types}")
            except Exception:
                pass
            metadata[key] = {
                "type": "path",
                "length": len(getattr(value, "relationships", [])),
            }

        # --- List of things (e.g., nodes or primitives) ---
        elif isinstance(value, list):
            # Render compactly; don’t inline whole Node objects
            preview = []
            for item in value[:10]:  # preview first 10
                if isinstance(item, Node) or hasattr(item, "labels"):
                    preview.append({"node": {"labels": sorted(list(getattr(item, "labels", []))),
                                             "element_id": getattr(item, "element_id", None)}})
                elif isinstance(item, Relationship) or hasattr(item, "type"):
                    preview.append({"relationship": {"type": getattr(item, "type", None)}})
                else:
                    preview.append(item)
            content_lines.append(f"- {key} (list, preview): {preview}")
            metadata[key] = {"type": "list", "size": len(value)}

        # --- Dict (map) from Cypher ---
        elif isinstance(value, dict):
            content_lines.append(f"### Map `{key}`")
            content_lines += _format_props(value)
            metadata[key] = {"type": "map", "size": len(value)}

        # --- Primitive / other ---
        else:
            content_lines.append(f"- {key}: {value}")
            metadata[key] = value

        content_lines.append("")  # blank line

    content = "\n".join(content_lines)
    return RetrieverResultItem(content=content, metadata=metadata)

def parse_user_info(user_info: dict) -> str:
    """
    Parses user information dictionary into a formatted string.

    Args:
        user_info (dict): A dictionary containing user information. Keys expected are position("Cabin Crew", "Pilot"), age(int), gender("F", "M")

    Returns:
        str: A formatted string representation of the user information.
    """
    info_lines = []
    for key, value in user_info.items():
        info_lines.append(f"- {key}: {value}")

    return "\n".join(info_lines)
