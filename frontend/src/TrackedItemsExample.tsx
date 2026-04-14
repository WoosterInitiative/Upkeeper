import React, { useState, useEffect } from 'react';
import type {
  TrackedItemResponse,
  TrackedItemCreateRequest,
  TagResponse
} from './api/types.gen';
import {
  listTrackedItemsItemsGet,
  createTrackedItemItemsPost,
  listTagsTagsGet,
  deleteTrackedItemItemsSlugDelete
} from './api/sdk.gen';

export const TrackedItemsExample: React.FC = () => {
  const [items, setItems] = useState<TrackedItemResponse[]>([]);
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [newItemName, setNewItemName] = useState('');

  // Load items and tags on component mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Use generated client functions with proper typing
        const [itemsResponse, tagsResponse] = await Promise.all([
          listTrackedItemsItemsGet(),
          listTagsTagsGet()
        ]);

        setItems(itemsResponse.data || []);
        setTags(tagsResponse.data || []);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Create new tracked item
  const handleCreateItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemName.trim()) return;

    try {
      setLoading(true);

      // Create request payload with proper typing
      const createRequest: TrackedItemCreateRequest = {
        name: newItemName.trim(),
        attributes: {
          category: 'user-created',
          timestamp: new Date().toISOString()
        }
      };

      // Use generated client function
      const response = await createTrackedItemItemsPost({
        body: createRequest
      });

      if (response.data) {
        setItems(prev => [...prev, response.data]);
        setNewItemName('');
      }
    } catch (error) {
      console.error('Failed to create item:', error);
    } finally {
      setLoading(false);
    }
  };

  // Delete item
  const handleDeleteItem = async (slug: string) => {
    try {
      setLoading(true);

      // Use generated client function with path parameter
      await deleteTrackedItemItemsSlugDelete({
        path: { slug }
      });

      setItems(prev => prev.filter(item => item.slug !== slug));
    } catch (error) {
      console.error('Failed to delete item:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tracked-items">
      <h2>Tracked Items</h2>

      {/* Create new item form */}
      <form onSubmit={handleCreateItem}>
        <input
          type="text"
          value={newItemName}
          onChange={(e) => setNewItemName(e.target.value)}
          placeholder="Enter item name"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !newItemName.trim()}>
          {loading ? 'Creating...' : 'Create Item'}
        </button>
      </form>

      {/* Items list */}
      <div className="items-list">
        {loading && items.length === 0 && <p>Loading...</p>}

        {items.map((item) => (
          <div key={item.id} className="item-card">
            <h3>{item.name}</h3>
            <p>
              <strong>Slug:</strong> {item.slug}
            </p>
            {item.location && (
              <p>
                <strong>Location:</strong> {item.location}
              </p>
            )}
            {item.notes && (
              <p>
                <strong>Notes:</strong> {item.notes}
              </p>
            )}
            <div className="item-meta">
              <small>
                Created: {new Date(item.createdAt).toLocaleDateString()}
                {item.updatedAt !== item.createdAt && (
                  <> | Updated: {new Date(item.updatedAt).toLocaleDateString()}</>
                )}
              </small>
            </div>
            <button
              onClick={() => handleDeleteItem(item.slug)}
              disabled={loading}
              className="delete-button"
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      {/* Tags display */}
      {tags.length > 0 && (
        <div className="tags-section">
          <h3>Available Tags</h3>
          <div className="tags-list">
            {tags.map((tag) => (
              <span key={tag.id} className="tag-badge">
                {tag.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrackedItemsExample;
