/**
 * Resizable Image Extension for Tiptap
 * Allows users to resize images by dragging corners
 */

import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer, NodeViewWrapper } from '@tiptap/react';
import React, { useState, useRef, useEffect } from 'react';

// React component for resizable image
const ResizableImageComponent = ({ node, updateAttributes, selected }) => {
  const [isResizing, setIsResizing] = useState(false);
  const [dimensions, setDimensions] = useState({
    width: node.attrs.width || 300,
    height: node.attrs.height || 'auto',
  });
  const imgRef = useRef(null);
  const startPos = useRef({ x: 0, y: 0, width: 0, height: 0 });

  // Debug: Log node attributes on mount
  useEffect(() => {
    console.log('🖼️ ResizableImage mounted with attributes:', {
      src: node.attrs.src?.substring(0, 50) + '...',
      width: node.attrs.width,
      height: node.attrs.height,
      alt: node.attrs.alt,
    });
  }, []);

  const handleMouseDown = (e, corner) => {
    e.preventDefault();
    e.stopPropagation();
    
    setIsResizing(true);
    
    const img = imgRef.current;
    if (!img) return;

    startPos.current = {
      x: e.clientX,
      y: e.clientY,
      width: img.offsetWidth,
      height: img.offsetHeight,
    };

    const handleMouseMove = (moveEvent) => {
      const deltaX = moveEvent.clientX - startPos.current.x;
      const deltaY = moveEvent.clientY - startPos.current.y;
      
      let newWidth = startPos.current.width;
      
      // Calculate new width based on corner being dragged
      if (corner === 'se' || corner === 'sw') {
        // Bottom corners
        newWidth = corner === 'se' 
          ? startPos.current.width + deltaX
          : startPos.current.width - deltaX;
      } else {
        // Top corners  
        newWidth = corner === 'ne'
          ? startPos.current.width + deltaX
          : startPos.current.width - deltaX;
      }
      
      // Enforce minimum and maximum width
      newWidth = Math.max(100, Math.min(800, newWidth));
      
      setDimensions({
        width: newWidth,
        height: 'auto', // Maintain aspect ratio
      });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      
      // Save the final dimensions to node attributes
      updateAttributes({
        width: dimensions.width,
        height: dimensions.height,
      });
      
      console.log('🖼️ Image resized to:', dimensions.width, 'x', dimensions.height);
      
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // Update dimensions when attributes change
  useEffect(() => {
    if (node.attrs.width) {
      setDimensions({
        width: node.attrs.width,
        height: node.attrs.height || 'auto',
      });
    }
  }, [node.attrs.width, node.attrs.height]);

  return (
    <NodeViewWrapper className="resizable-image-wrapper" style={{ display: 'inline-block', position: 'relative' }}>
      <img
        ref={imgRef}
        src={node.attrs.src}
        alt={node.attrs.alt || ''}
        title={node.attrs.title || ''}
        style={{
          width: dimensions.width,
          height: dimensions.height,
          display: 'block',
          cursor: isResizing ? 'nwse-resize' : 'default',
        }}
        onLoad={() => {
          console.log('🖼️ Image rendered with dimensions:', {
            width: dimensions.width,
            height: dimensions.height,
            actualWidth: imgRef.current?.offsetWidth,
            actualHeight: imgRef.current?.offsetHeight,
          });
        }}
      />
      
      {/* Resize handles - only show when selected */}
      {selected && (
        <>
          {/* Top-left corner */}
          <div
            className="resize-handle resize-handle-nw"
            onMouseDown={(e) => handleMouseDown(e, 'nw')}
            style={{
              position: 'absolute',
              top: -4,
              left: -4,
              width: 12,
              height: 12,
              background: '#3b82f6',
              border: '2px solid white',
              borderRadius: '50%',
              cursor: 'nwse-resize',
              zIndex: 10,
            }}
          />
          
          {/* Top-right corner */}
          <div
            className="resize-handle resize-handle-ne"
            onMouseDown={(e) => handleMouseDown(e, 'ne')}
            style={{
              position: 'absolute',
              top: -4,
              right: -4,
              width: 12,
              height: 12,
              background: '#3b82f6',
              border: '2px solid white',
              borderRadius: '50%',
              cursor: 'nesw-resize',
              zIndex: 10,
            }}
          />
          
          {/* Bottom-left corner */}
          <div
            className="resize-handle resize-handle-sw"
            onMouseDown={(e) => handleMouseDown(e, 'sw')}
            style={{
              position: 'absolute',
              bottom: -4,
              left: -4,
              width: 12,
              height: 12,
              background: '#3b82f6',
              border: '2px solid white',
              borderRadius: '50%',
              cursor: 'nesw-resize',
              zIndex: 10,
            }}
          />
          
          {/* Bottom-right corner */}
          <div
            className="resize-handle resize-handle-se"
            onMouseDown={(e) => handleMouseDown(e, 'se')}
            style={{
              position: 'absolute',
              bottom: -4,
              right: -4,
              width: 12,
              height: 12,
              background: '#3b82f6',
              border: '2px solid white',
              borderRadius: '50%',
              cursor: 'nwse-resize',
              zIndex: 10,
            }}
          />
        </>
      )}
    </NodeViewWrapper>
  );
};

// Tiptap extension
export const ResizableImage = Node.create({
  name: 'resizableImage',
  
  group: 'block',
  
  draggable: true,
  
  addAttributes() {
    return {
      src: {
        default: null,
        parseHTML: element => element.getAttribute('src'),
        renderHTML: attributes => {
          if (!attributes.src) return {};
          return { src: attributes.src };
        },
      },
      alt: {
        default: null,
        parseHTML: element => element.getAttribute('alt'),
        renderHTML: attributes => {
          if (!attributes.alt) return {};
          return { alt: attributes.alt };
        },
      },
      title: {
        default: null,
        parseHTML: element => element.getAttribute('title'),
        renderHTML: attributes => {
          if (!attributes.title) return {};
          return { title: attributes.title };
        },
      },
      width: {
        default: 300,
        parseHTML: element => {
          const width = element.getAttribute('width');
          return width ? parseInt(width, 10) : 300;
        },
        renderHTML: attributes => {
          if (!attributes.width) return {};
          return { width: attributes.width };
        },
      },
      height: {
        default: 'auto',
        parseHTML: element => element.getAttribute('height') || 'auto',
        renderHTML: attributes => {
          if (!attributes.height || attributes.height === 'auto') return { height: 'auto' };
          return { height: attributes.height };
        },
      },
    };
  },
  
  parseHTML() {
    return [
      {
        tag: 'img[src]',
        getAttrs: dom => {
          console.log('🔍 Parsing img tag with attributes:', {
            src: dom.getAttribute('src')?.substring(0, 50) + '...',
            width: dom.getAttribute('width'),
            height: dom.getAttribute('height'),
            alt: dom.getAttribute('alt'),
          });
          return {
            src: dom.getAttribute('src'),
            alt: dom.getAttribute('alt'),
            title: dom.getAttribute('title'),
            width: dom.getAttribute('width') ? parseInt(dom.getAttribute('width'), 10) : 300,
            height: dom.getAttribute('height') || 'auto',
          };
        },
      },
    ];
  },
  
  renderHTML({ HTMLAttributes }) {
    return ['img', mergeAttributes(HTMLAttributes)];
  },
  
  addNodeView() {
    return ReactNodeViewRenderer(ResizableImageComponent);
  },
  
  addCommands() {
    return {
      setResizableImage: (options) => ({ commands }) => {
        return commands.insertContent({
          type: this.name,
          attrs: options,
        });
      },
    };
  },
});

export default ResizableImage;
