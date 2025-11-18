import React from 'react';
import { NodeResizer } from '@xyflow/react';
import NoteBlock from './NoteBlock';

const NoteBlockWithResizer = (props) => {
  return (
    <>
      {/* Resize handles - only show when selected */}
      <NodeResizer
        isVisible={props.selected}
        minWidth={200}
        minHeight={150}
        handleClassName="custom-resize-handle"
      />
      
      {/* The actual NoteBlock component */}
      <NoteBlock {...props} />
    </>
  );
};

export default NoteBlockWithResizer;
