/**
 * 👥 Friends API Service for Web App
 * Handles all Friends, Households, and Collaboration API calls
 * Adapted from mobile app with web-specific patterns
 */

class FriendsAPI {
  static BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

  /**
   * Make authenticated API request
   */
  static async authenticatedRequest(endpoint, options = {}) {
    try {
      const token = localStorage.getItem('authToken'); // Fixed: was 'token', should be 'authToken'
      
      console.log('🔍 FriendsAPI Debug:', {
        endpoint: endpoint,
        BASE_URL: this.BASE_URL,
        fullURL: `${this.BASE_URL}${endpoint}`,
        hasToken: !!token,
        tokenPreview: token ? token.substring(0, 20) + '...' : 'none'
      });
      
      const response = await fetch(`${this.BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
          ...(options.headers || {})
        }
      });
      
      console.log('📡 FriendsAPI Response:', {
        status: response.status,
        ok: response.ok
      });
      
      const result = await response.json();
      
      if (!response.ok) {
        console.error('❌ FriendsAPI Error Response:', result);
        throw new Error(result.error || `HTTP ${response.status}`);
      }
      
      console.log('✅ FriendsAPI Success:', result);
      return result;
    } catch (error) {
      console.error(`❌ FriendsAPI request to ${endpoint} failed:`, error);
      throw error;
    }
  }

  // ================================================================
  // FRIENDS MANAGEMENT
  // ================================================================

  /**
   * Get user's friends list
   */
  static async getFriends() {
    try {
      const response = await this.authenticatedRequest('/api/friends/list');
      return {
        success: true,
        friends: response.friends || [],
        count: response.count || 0
      };
    } catch (error) {
      console.error('❌ Get friends error:', error);
      return {
        success: false,
        error: error.message || 'Failed to load friends',
        friends: []
      };
    }
  }

  /**
   * Get friend requests (incoming and outgoing)
   */
  static async getFriendRequests() {
    try {
      const response = await this.authenticatedRequest('/api/friends/requests');
      return {
        success: true,
        requests: response.requests || [],
        incoming_count: response.incoming_count || 0,
        outgoing_count: response.outgoing_count || 0
      };
    } catch (error) {
      console.error('❌ Get friend requests error:', error);
      return {
        success: false,
        error: error.message || 'Failed to load friend requests',
        requests: []
      };
    }
  }

  /**
   * Send friend request by email
   */
  static async sendFriendRequest(email, message = '') {
    try {
      const response = await this.authenticatedRequest('/api/friends/request', {
        method: 'POST',
        body: JSON.stringify({
          email: email.trim(),
          message: message.trim()
        })
      });
      
      return {
        success: true,
        message: response.message || 'Friend request sent!',
        request_id: response.request_id
      };
    } catch (error) {
      console.error('❌ Send friend request error:', error);
      return {
        success: false,
        error: error.message || 'Failed to send friend request'
      };
    }
  }

  /**
   * Accept friend request
   */
  static async acceptFriendRequest(requestId) {
    try {
      const response = await this.authenticatedRequest(`/api/friends/request/${requestId}/accept`, {
        method: 'POST'
      });
      
      return {
        success: true,
        message: response.message || 'Friend request accepted!'
      };
    } catch (error) {
      console.error('❌ Accept friend request error:', error);
      return {
        success: false,
        error: error.message || 'Failed to accept friend request'
      };
    }
  }

  /**
   * Decline friend request
   */
  static async declineFriendRequest(requestId) {
    try {
      const response = await this.authenticatedRequest(`/api/friends/request/${requestId}/decline`, {
        method: 'POST'
      });
      
      return {
        success: true,
        message: response.message || 'Friend request declined'
      };
    } catch (error) {
      console.error('❌ Decline friend request error:', error);
      return {
        success: false,
        error: error.message || 'Failed to decline friend request'
      };
    }
  }

  /**
   * Remove friend
   */
  static async removeFriend(friendId) {
    try {
      const response = await this.authenticatedRequest(`/api/friends/${friendId}/remove`, {
        method: 'DELETE'
      });
      
      return {
        success: true,
        message: response.message || 'Friend removed'
      };
    } catch (error) {
      console.error('❌ Remove friend error:', error);
      return {
        success: false,
        error: error.message || 'Failed to remove friend'
      };
    }
  }

  // ================================================================
  // HOUSEHOLDS MANAGEMENT
  // ================================================================

  /**
   * Get user's households
   */
  static async getHouseholds() {
    try {
      const response = await this.authenticatedRequest('/api/households/list');
      return {
        success: true,
        households: response.households || [],
        count: response.count || 0
      };
    } catch (error) {
      console.error('❌ Get households error:', error);
      return {
        success: false,
        error: error.message || 'Failed to load households',
        households: []
      };
    }
  }

  /**
   * Create new household
   */
  static async createHousehold(name, description = '') {
    try {
      const response = await this.authenticatedRequest('/api/households/create', {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim()
        })
      });
      
      return {
        success: true,
        message: response.message || 'Household created!',
        household: response.household
      };
    } catch (error) {
      console.error('❌ Create household error:', error);
      return {
        success: false,
        error: error.message || 'Failed to create household'
      };
    }
  }

  /**
   * Delete household
   */
  static async deleteHousehold(householdId) {
    try {
      const response = await this.authenticatedRequest(`/api/households/${householdId}/delete`, {
        method: 'DELETE'
      });
      
      return {
        success: true,
        message: response.message || 'Household deleted successfully'
      };
    } catch (error) {
      console.error('❌ Delete household error:', error);
      return {
        success: false,
        error: error.message || 'Failed to delete household'
      };
    }
  }

  /**
   * Add member to household
   */
  static async addHouseholdMember(householdId, friendId) {
    try {
      const response = await this.authenticatedRequest(`/api/households/${householdId}/members/add`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: friendId
        })
      });
      
      return {
        success: true,
        message: response.message || 'Member added to household'
      };
    } catch (error) {
      console.error('❌ Add household member error:', error);
      return {
        success: false,
        error: error.message || 'Failed to add member to household'
      };
    }
  }

  /**
   * Remove member from household
   */
  static async removeHouseholdMember(householdId, memberId) {
    try {
      const response = await this.authenticatedRequest(`/api/households/${householdId}/members/${memberId}/remove`, {
        method: 'DELETE'
      });
      
      return {
        success: true,
        message: response.message || 'Member removed from household'
      };
    } catch (error) {
      console.error('❌ Remove household member error:', error);
      return {
        success: false,
        error: error.message || 'Failed to remove member from household'
      };
    }
  }

  /**
   * Get household members
   */
  static async getHouseholdMembers(householdId) {
    try {
      const response = await this.authenticatedRequest(`/api/households/${householdId}/members`);
      return {
        success: true,
        members: response.members || []
      };
    } catch (error) {
      console.error('❌ Get household members error:', error);
      return {
        success: false,
        error: error.message || 'Failed to load household members',
        members: []
      };
    }
  }

  // ================================================================
  // UTILITY FUNCTIONS
  // ================================================================

  /**
   * Check if Friends API is available
   */
  static async isAvailable() {
    try {
      await this.authenticatedRequest('/api/friends/list');
      return true;
    } catch (error) {
      console.log('ℹ️ Friends API not available, will use fallback');
      return false;
    }
  }
}

export default FriendsAPI;