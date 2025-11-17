"""
Knowledge Graph Service
Manages the knowledge graph visualization and related concept extraction
"""

import json
from typing import List, Dict, Optional
from anthropic import Anthropic
import os


class KnowledgeGraphService:
    """Service for building and managing knowledge graphs"""

    def __init__(self):
        """Initialize the knowledge graph service"""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"
        else:
            self.client = None

    def extract_related_concepts(self, topic: str, conversation_history: List[Dict]) -> List[str]:
        """
        Extract related concepts from a teaching session using Claude

        Args:
            topic: Main topic being taught
            conversation_history: List of conversation turns

        Returns:
            List of related concept names
        """
        if not self.client:
            return []

        # Build conversation context
        conversation_text = ""
        for turn in conversation_history[-5:]:  # Last 5 turns
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            conversation_text += f"{role.capitalize()}: {content}\n\n"

        prompt = f"""Based on this teaching conversation about "{topic}", identify 3-5 related concepts or topics that were mentioned or are closely related.

Conversation:
{conversation_text}

Return ONLY a JSON array of concept names (strings), no additional text.
Example: ["concept1", "concept2", "concept3"]

Related concepts:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            concepts_text = response.content[0].text.strip()
            concepts = json.loads(concepts_text)

            # Filter out the main topic and validate
            related = [c for c in concepts if isinstance(c, str) and c.lower() != topic.lower()]
            return related[:5]  # Max 5 concepts

        except Exception as e:
            print(f"Error extracting related concepts: {e}")
            return []

    def generate_graph_html(self, graph_data: Dict) -> str:
        """
        Generate HTML for interactive knowledge graph visualization using vis.js

        Args:
            graph_data: Dictionary with "nodes" and "edges" lists

        Returns:
            HTML string for rendering the graph
        """
        nodes_json = json.dumps(graph_data.get("nodes", []))
        edges_json = json.dumps(graph_data.get("edges", []))

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #mynetwork {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            background: #fafafa;
            border-radius: 8px;
        }}
        .legend {{
            margin-top: 10px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
        .color-box {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            border-radius: 3px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    <div class="legend">
        <div class="legend-item">
            <span class="color-box" style="background: #97C2FC;"></span>
            <span>Low Confidence (&lt;50%)</span>
        </div>
        <div class="legend-item">
            <span class="color-box" style="background: #FFCC00;"></span>
            <span>Medium Confidence (50-75%)</span>
        </div>
        <div class="legend-item">
            <span class="color-box" style="background: #7BE141;"></span>
            <span>High Confidence (&gt;75%)</span>
        </div>
        <div class="legend-item">
            <span><strong>Node Size</strong> = Times Taught</span>
        </div>
    </div>

    <script type="text/javascript">
        // Parse data
        var rawNodes = {nodes_json};
        var rawEdges = {edges_json};

        // Process nodes for visualization
        var nodes = rawNodes.map(function(node) {{
            // Determine color based on confidence
            var color = '#97C2FC';  // Blue - low confidence
            if (node.confidence >= 0.75) {{
                color = '#7BE141';  // Green - high confidence
            }} else if (node.confidence >= 0.50) {{
                color = '#FFCC00';  // Yellow - medium confidence
            }}

            // Size based on times taught (min 20, max 60)
            var size = Math.min(Math.max(20 + node.times_taught * 5, 20), 60);

            return {{
                id: node.id,
                label: node.label,
                title: 'Topic: ' + node.label +
                       '\\nTimes Taught: ' + node.times_taught +
                       '\\nConfidence: ' + (node.confidence * 100).toFixed(0) + '%' +
                       '\\nClarity: ' + (node.clarity * 100).toFixed(0) + '%' +
                       (node.gaps && node.gaps.length > 0 ? '\\n\\nGaps:\\n- ' + node.gaps.join('\\n- ') : ''),
                color: {{
                    background: color,
                    border: '#2B7CE9',
                    highlight: {{
                        background: color,
                        border: '#2B7CE9'
                    }}
                }},
                size: size,
                font: {{
                    size: 14,
                    color: '#000000'
                }}
            }};
        }});

        // Process edges
        var edges = rawEdges.map(function(edge) {{
            // Edge width based on strength
            var width = Math.max(1, edge.strength || 1);

            return {{
                from: edge.from,
                to: edge.to,
                label: edge.type || 'related_to',
                width: width,
                arrows: 'to',
                color: {{
                    color: '#848484',
                    highlight: '#2B7CE9'
                }},
                font: {{
                    size: 10,
                    align: 'middle'
                }}
            }};
        }});

        // Create network
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: new vis.DataSet(nodes),
            edges: new vis.DataSet(edges)
        }};

        var options = {{
            nodes: {{
                shape: 'dot',
                font: {{
                    size: 14,
                    face: 'Arial'
                }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                smooth: {{
                    type: 'continuous'
                }},
                arrows: {{
                    to: {{
                        enabled: true,
                        scaleFactor: 0.5
                    }}
                }}
            }},
            physics: {{
                stabilization: {{
                    iterations: 200
                }},
                barnesHut: {{
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 150,
                    springConstant: 0.04
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                zoomView: true,
                dragView: true
            }}
        }};

        var network = new vis.Network(container, data, options);

        // Add click event
        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var node = nodes.find(n => n.id === nodeId);
                console.log("Clicked node:", node);
            }}
        }});
    </script>
</body>
</html>
"""
        return html
