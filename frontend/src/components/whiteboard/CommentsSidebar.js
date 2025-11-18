/**
 * Comments Sidebar Component
 * Real-time comments for whiteboard objects using Pusher
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { subscribeToWhiteboard, unsubscribeFromWhiteboard } from '../../utils/pusher';
import { apiCall } from '../../utils/api';
import './CommentsSidebar.css';

const CommentsSidebar = ({ 
  whiteboardId,
  selectedObject,
  isOpen,
  onClose 
}) => {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [replyingTo, setReplyingTo] = useState(null);
  const commentsEndRef = useRef(null);
  
  // Scroll to bottom when comments change
  const scrollToBottom = () => {
    commentsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(scrollToBottom, [comments]);
  
  // Fetch comments when object is selected
  useEffect(() => {
    if (!selectedObject || !whiteboardId) {
      setComments([]);
      return;
    }
    
    console.log('🎯 Selected object for comments:', selectedObject);
    
    fetchComments();
  }, [selectedObject, whiteboardId]);
  
  // Subscribe to Pusher for real-time updates
  useEffect(() => {
    if (!whiteboardId) return;
    
    const channel = subscribeToWhiteboard(whiteboardId, {
      onCommentCreated: (data) => {
        console.log('💬 New comment received via Pusher:', data);
        // Only add if it's for the currently selected object
        if (selectedObject && 
            data.object_type === selectedObject.type && 
            data.object_id === selectedObject.id) {
          setComments(prev => {
            // Check if comment already exists (avoid duplicates)
            if (prev.find(c => c.id === data.id)) {
              return prev;
            }
            return [...prev, data];
          });
        }
      },
      
      onCommentUpdated: (data) => {
        console.log('✏️ Comment updated via Pusher:', data);
        setComments(prev => prev.map(c => c.id === data.id ? data : c));
      },
      
      onCommentDeleted: (data) => {
        console.log('🗑️ Comment deleted via Pusher:', data);
        console.log('🗑️ Comment ID to delete:', data.comment_id);
        console.log('🗑️ Current comments:', comments);
        setComments(prev => {
          const filtered = prev.filter(c => c.id !== data.comment_id);
          console.log('🗑️ After filter:', filtered);
          return filtered;
        });
      },
    });
    
    return () => {
      unsubscribeFromWhiteboard(whiteboardId);
    };
  }, [whiteboardId, selectedObject]);
  
  const fetchComments = async () => {
    if (!selectedObject) return;
    
    setLoading(true);
    try {
      const response = await apiCall(
        `/api/v2/comments?whiteboard_id=${whiteboardId}&object_type=${selectedObject.type}&object_id=${selectedObject.id}`,
        { method: 'GET' }
      );
      
      if (response.success) {
        setComments(response.comments || []);
      }
    } catch (error) {
      console.error('Error fetching comments:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSubmitComment = async (e) => {
    e.preventDefault();
    
    if (!newComment.trim() || !selectedObject) {
      console.log('❌ Cannot submit:', { hasComment: !!newComment.trim(), hasObject: !!selectedObject });
      return;
    }
    
    console.log('📤 Submitting comment:', {
      selectedObject,
      object_type: selectedObject.type,
      object_id: selectedObject.id,
      whiteboard_id: whiteboardId,
      content: newComment.trim()
    });
    
    try {
      const response = await apiCall('/api/v2/comments', {
        method: 'POST',
        body: JSON.stringify({
          whiteboard_id: whiteboardId,
          object_type: selectedObject.type,
          object_id: selectedObject.id,
          content: newComment.trim(),
          parent_id: replyingTo?.id || null,
        }),
      });
      
      console.log('📥 Comment response:', response);
      
      if (response.success) {
        setNewComment('');
        setReplyingTo(null);
        // Add comment immediately to local state (optimistic update)
        setComments(prev => {
          // Check if it already exists from Pusher
          if (prev.find(c => c.id === response.comment.id)) {
            return prev;
          }
          return [...prev, response.comment];
        });
      } else {
        console.error('❌ Failed to post comment:', response);
      }
    } catch (error) {
      console.error('❌ Error posting comment:', error);
    }
  };
  
  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Delete this comment?')) return;
    
    try {
      // Optimistically remove from UI
      setComments(prev => prev.filter(c => c.id !== commentId));
      
      const response = await apiCall(`/api/v2/comments/${commentId}`, {
        method: 'DELETE',
      });
      
      if (!response.success) {
        // If delete failed, refetch to restore state
        console.error('❌ Delete failed:', response);
        fetchComments();
      }
    } catch (error) {
      console.error('Error deleting comment:', error);
      // Refetch on error to restore state
      fetchComments();
    }
  };
  
  const getObjectName = () => {
    if (!selectedObject) return '';
    
    switch (selectedObject.type) {
      case 'recipe':
        return selectedObject.data?.title || 'Recipe';
      case 'meal_plan':
        return selectedObject.data?.name || 'Meal Plan';
      case 'grocery_list':
        return selectedObject.data?.name || 'Grocery List';
      default:
        return 'Object';
    }
  };
  
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };
  
  const getUserInitials = (username) => {
    if (!username) return '?';
    return username.substring(0, 2).toUpperCase();
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="comments-sidebar">
      {/* Header */}
      <div className="comments-header">
        <div>
          <h3>Comments</h3>
          {selectedObject && (
            <p className="selected-object-name">{getObjectName()}</p>
          )}
        </div>
        <button className="close-button" onClick={onClose}>
          ✕
        </button>
      </div>
      
      {/* Comments List */}
      <div className="comments-list">
        {loading ? (
          <div className="loading-message">Loading comments...</div>
        ) : !selectedObject ? (
          <div className="empty-message">
            Select an object to view comments
          </div>
        ) : comments.length === 0 ? (
          <div className="empty-message">
            No comments yet. Be the first to comment!
          </div>
        ) : (
          comments.map(comment => (
            <div key={comment.id} className="comment">
              <div className="comment-avatar">
                {comment.user?.avatar_url ? (
                  <img src={comment.user.avatar_url} alt={comment.user.name} />
                ) : (
                  <div className="avatar-placeholder">
                    {getUserInitials(comment.user?.name)}
                  </div>
                )}
              </div>
              
              <div className="comment-content">
                <div className="comment-header">
                  <span className="comment-author">
                    {comment.user?.name || 'Unknown User'}
                  </span>
                  <span className="comment-time">
                    {formatTime(comment.created_at)}
                  </span>
                </div>
                
                <p className="comment-text">{comment.content}</p>
                
                <div className="comment-actions">
                  <button 
                    className="comment-action-btn"
                    onClick={() => setReplyingTo(comment)}
                  >
                    Reply
                  </button>
                  
                  {comment.user_id === user?.id && (
                    <button 
                      className="comment-action-btn delete"
                      onClick={() => handleDeleteComment(comment.id)}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={commentsEndRef} />
      </div>
      
      {/* Comment Input */}
      {selectedObject && (
        <form className="comment-input-form" onSubmit={handleSubmitComment}>
          {replyingTo && (
            <div className="replying-to">
              Replying to {replyingTo.user?.name}
              <button 
                type="button" 
                onClick={() => setReplyingTo(null)}
                className="cancel-reply"
              >
                ✕
              </button>
            </div>
          )}
          
          <div className="comment-input-container">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a comment..."
              className="comment-input"
              rows={3}
            />
            
            <button 
              type="submit" 
              className="send-button"
              disabled={!newComment.trim()}
            >
              Send
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default CommentsSidebar;
