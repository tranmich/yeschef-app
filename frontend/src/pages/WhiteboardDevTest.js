import React, { useEffect, useState } from 'react';
import WhiteboardApp from './WhiteboardApp';
import { WhiteboardProvider } from '../contexts/WhiteboardContext';
import { RecipeCacheProvider, useRecipeCache } from '../contexts/RecipeCacheContext';
import { useWhiteboard } from '../contexts/WhiteboardContext';
import { useWhiteboardData } from '../hooks/useWhiteboardData';
import { useRecipeNodes } from '../hooks/useRecipeNodes';
import { validateNode, normalizeNode } from '../utils/nodeValidation';

// Simple inline logger component for visual feedback
function LogPanel({ logs }) {
  return (
    <div style={{
      position: 'fixed',
      right: 0,
      bottom: 0,
      width: '480px',
      maxHeight: '50vh',
      overflow: 'auto',
      background: '#0b1120',
      color: '#e5e7eb',
      fontFamily: 'monospace',
      fontSize: '11px',
      padding: '8px',
      borderTopLeftRadius: '6px',
      boxShadow: '0 0 10px rgba(0,0,0,0.4)',
      zIndex: 9999,
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Whiteboard Dev Test Log</div>
      {logs.map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
    </div>
  );
}

function WhiteboardDevHarness() {
  const { cacheVersion, getCacheStats, addRecipes } = useRecipeCache();
  const {
    whiteboardId,
    nodes,
    addNode,
    addNodes,
    commentCounts,
  } = useWhiteboard();

  const { loadWhiteboard } = useWhiteboardData();
  const {
    addRecipe,
    addRecipes: addRecipesToCanvas,
    getAllRecipeNodes,
  } = useRecipeNodes();

  const [logs, setLogs] = useState([]);

  const log = (msg) => {
    setLogs((prev) => [...prev, `${new Date().toISOString()} - ${msg}`].slice(-80));
  };

  // Basic smoke tests on mount
  useEffect(() => {
    (async () => {
      log(`DEV HARNESS START – whiteboardId=${whiteboardId || 'none'}`);

      // 1) Validate nodeValidation works with a minimal note node
      try {
        const rawNode = {
          id: 'note-test-1',
          type: 'note',
          position: { x: 10, y: 20 },
          data: {
            object_id: 1,
            name: 'Test Note',
            content: '<p>hello</p>',
          },
        };
        validateNode(rawNode);
        const normalized = normalizeNode(rawNode);
        addNode(normalized);
        log('✅ validateNode/normalizeNode passed for basic note node');
      } catch (e) {
        log(`❌ validateNode failed: ${e.message}`);
      }

      // 2) Exercise RecipeCache directly
      const fakeRecipe = {
        id: 9999,
        title: 'Dev Harness Recipe',
        image_url: null,
        prep_time: 5,
        cook_time: 10,
        total_time: 15,
        category: 'dev',
      };
      addRecipes([fakeRecipe]);
      const stats = getCacheStats();
      log(`📦 Recipe cache size after addRecipes: ${stats.size}`);

      // 3) If a real whiteboardId is provided, try loading it
      if (whiteboardId) {
        try {
          await loadWhiteboard();
          log('✅ loadWhiteboard completed without throwing');
          log(`📊 Nodes after loadWhiteboard: ${nodes.length}`);
        } catch (e) {
          log(`❌ loadWhiteboard threw: ${e.message}`);
        }
      } else {
        log('ℹ️ No whiteboardId passed – skipping live loadWhiteboard test');
      }

      // 4) Exercise recipe node helpers with a fake in-cache recipe
      try {
        const position = { x: 400, y: 200 };
        await addRecipe(fakeRecipe, position);
        const recipeNodes = getAllRecipeNodes();
        log(`🍕 Recipe nodes on canvas after addRecipe(fake): ${recipeNodes.length}`);
      } catch (e) {
        log(`❌ addRecipe(fake) failed: ${e.message}`);
      }

      log(`💬 Comment counts keys: ${Object.keys(commentCounts || {}).join(', ') || '(none)'}`);
      log('✅ Dev harness finished – check UI and logs');
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <LogPanel logs={logs} />;
}

// Top-level page: wraps real WhiteboardApp with providers + harness
export default function WhiteboardDevTestPage(props) {
  // For dev you can hard-code ids or pass via route
  const devWhiteboardId = props.whiteboardId || null;
  const devHouseholdId = props.householdId || null;

  return (
    <RecipeCacheProvider>
      <WhiteboardProvider whiteboardId={devWhiteboardId} householdId={devHouseholdId}>
        <div style={{ position: 'relative', width: '100%', height: '100vh' }}>
          <WhiteboardApp {...props} />
          <WhiteboardDevHarness />
        </div>
      </WhiteboardProvider>
    </RecipeCacheProvider>
  );
}
