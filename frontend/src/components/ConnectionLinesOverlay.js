/**
 * Connection Lines Overlay
 * ========================
 * SVG lines connecting recipe cards to grocery list widgets
 * 
 * Features:
 * - Animated dashed lines
 * - Auto-updates as cards/widgets move
 * - Hover highlighting
 * - Toggle visibility
 * 
 * Author: GitHub Copilot
 * Date: November 4, 2025
 */

import React, { useState, useEffect } from 'react';
import './ConnectionLinesOverlay.css';

const ConnectionLinesOverlay = ({
  groceryListWidgets = [],
  nodes = [],
  visible = true,
  canvasViewport = { x: 0, y: 0, zoom: 1 } // Pass viewport from ReactFlow
}) => {
  const [lines, setLines] = useState([]);
  const [hoveredLine, setHoveredLine] = useState(null);

  // Calculate line positions
  useEffect(() => {
    const calculatedLines = [];

    groceryListWidgets.forEach(widget => {
      // Get widget position (in canvas coordinates)
      const widgetX = widget.position.x;
      const widgetY = widget.position.y + 24; // Center of header

      // Use linkedRecipeIds for persistent connections
      const recipeIds = widget.linkedRecipeIds || widget.linkedRecipes.map(r => r.id);

      // For each linked recipe, find the current node by recipe_id
      recipeIds.forEach(recipeId => {
        // Find node by recipe_id (persistent even if node is recreated)
        const node = nodes.find(n => n.data?.recipe_id === recipeId);
        
        if (node) {
          // Get recipe card position (in canvas coordinates - no viewport transformation needed!)
          const cardX = node.position.x + 300; // Card width = 300
          const cardY = node.position.y + 200; // Card height / 2 = 200

          calculatedLines.push({
            id: `line-${widget.id}-${recipeId}`,
            widgetId: widget.id,
            recipeId: recipeId,
            nodeId: node.id,
            recipeTitle: node.data.title || node.data.name,
            x1: cardX,
            y1: cardY,
            x2: widgetX,
            y2: widgetY
          });
        }
      });
    });

    setLines(calculatedLines);
  }, [groceryListWidgets, nodes]);

  if (!visible || lines.length === 0) {
    return null;
  }

  return (
    <svg className="connection-lines-overlay">
      <defs>
        {/* Animated dashed line pattern */}
        <pattern
          id="dashedPattern"
          patternUnits="userSpaceOnUse"
          width="10"
          height="1"
        >
          <line
            x1="0"
            y1="0"
            x2="5"
            y2="0"
            stroke="#AAC6AD"
            strokeWidth="2"
          />
        </pattern>

        {/* Glow filter for hover */}
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>

        {/* Arrow marker */}
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3, 0 6"
            fill="#AAC6AD"
          />
        </marker>

        {/* Hovered arrow marker (brighter) */}
        <marker
          id="arrowhead-hover"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3, 0 6"
            fill="#7ea982"
          />
        </marker>
      </defs>

      {/* Draw all connection lines */}
      {lines.map(line => {
        const isHovered = hoveredLine === line.id;
        
        return (
          <g key={line.id}>
            {/* Invisible thick line for easier hovering */}
            <line
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke="transparent"
              strokeWidth="20"
              onMouseEnter={() => setHoveredLine(line.id)}
              onMouseLeave={() => setHoveredLine(null)}
              style={{ cursor: 'pointer' }}
            />
            
            {/* Visible dashed line */}
            <line
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke={isHovered ? "#7ea982" : "#AAC6AD"}
              strokeWidth={isHovered ? "3" : "2"}
              strokeDasharray="8 4"
              opacity={isHovered ? "1" : "0.6"}
              markerEnd={isHovered ? "url(#arrowhead-hover)" : "url(#arrowhead)"}
              filter={isHovered ? "url(#glow)" : "none"}
              className="connection-line"
              style={{
                transition: 'all 0.2s ease',
                pointerEvents: 'none'
              }}
            >
              {/* Animate the dash offset for movement effect */}
              <animate
                attributeName="stroke-dashoffset"
                from="0"
                to="12"
                dur="1s"
                repeatCount="indefinite"
              />
            </line>

            {/* Tooltip on hover */}
            {isHovered && (
              <g>
                <rect
                  x={(line.x1 + line.x2) / 2 - 60}
                  y={(line.y1 + line.y2) / 2 - 15}
                  width="120"
                  height="30"
                  rx="6"
                  fill="white"
                  stroke="#AAC6AD"
                  strokeWidth="2"
                  style={{ pointerEvents: 'none' }}
                />
                <text
                  x={(line.x1 + line.x2) / 2}
                  y={(line.y1 + line.y2) / 2 + 5}
                  textAnchor="middle"
                  fontSize="12"
                  fontWeight="600"
                  fill="#374151"
                  style={{ pointerEvents: 'none' }}
                >
                  {line.recipeTitle.length > 15 
                    ? line.recipeTitle.substring(0, 15) + '...' 
                    : line.recipeTitle}
                </text>
              </g>
            )}
          </g>
        );
      })}
    </svg>
  );
};

export default ConnectionLinesOverlay;
