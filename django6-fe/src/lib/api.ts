import type {
  Platform,
  Tag,
  Collection,
  Content,
  ContentListItem,
  SearchHistory,
  Stats,
  PaginatedResponse,
  SearchParams,
  BulkImportRequest,
  BulkImportResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Token ${this.token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // Platforms
  async getPlatforms(): Promise<Platform[]> {
    return this.request<Platform[]>('/platforms/');
  }

  async getPlatformStats(slug: string): Promise<{
    total_contents: number;
    by_type: Record<string, number>;
    favorites: number;
  }> {
    return this.request(`/platforms/${slug}/stats/`);
  }

  // Tags
  async getTags(): Promise<Tag[]> {
    return this.request<Tag[]>('/tags/');
  }

  async getPopularTags(): Promise<Tag[]> {
    return this.request<Tag[]>('/tags/popular/');
  }

  async createTag(data: { name: string; color?: string }): Promise<Tag> {
    return this.request<Tag>('/tags/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteTag(slug: string): Promise<void> {
    await this.request(`/tags/${slug}/`, { method: 'DELETE' });
  }

  // Collections
  async getCollections(): Promise<Collection[]> {
    return this.request<Collection[]>('/collections/');
  }

  async createCollection(data: {
    name: string;
    description?: string;
  }): Promise<Collection> {
    return this.request<Collection>('/collections/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCollection(
    id: number,
    data: Partial<Collection>
  ): Promise<Collection> {
    return this.request<Collection>(`/collections/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteCollection(id: number): Promise<void> {
    await this.request(`/collections/${id}/`, { method: 'DELETE' });
  }

  async addToCollection(
    collectionId: number,
    contentIds: number[]
  ): Promise<{ added: number }> {
    return this.request(`/collections/${collectionId}/add_content/`, {
      method: 'POST',
      body: JSON.stringify({ content_ids: contentIds }),
    });
  }

  async removeFromCollection(
    collectionId: number,
    contentIds: number[]
  ): Promise<{ removed: number }> {
    return this.request(`/collections/${collectionId}/remove_content/`, {
      method: 'POST',
      body: JSON.stringify({ content_ids: contentIds }),
    });
  }

  // Contents
  async getContents(params?: {
    type?: string;
    platform?: string;
    tags?: string[];
    collection?: number;
    favorites?: boolean;
    include_archived?: boolean;
    page?: number;
  }): Promise<PaginatedResponse<ContentListItem>> {
    const searchParams = new URLSearchParams();
    if (params?.type) searchParams.set('type', params.type);
    if (params?.platform) searchParams.set('platform', params.platform);
    if (params?.tags) params.tags.forEach((t) => searchParams.append('tags', t));
    if (params?.collection) searchParams.set('collection', String(params.collection));
    if (params?.favorites) searchParams.set('favorites', 'true');
    if (params?.include_archived) searchParams.set('include_archived', 'true');
    if (params?.page) searchParams.set('page', String(params.page));

    const query = searchParams.toString();
    return this.request<PaginatedResponse<ContentListItem>>(
      `/contents/${query ? `?${query}` : ''}`
    );
  }

  async getContent(id: number): Promise<Content> {
    return this.request<Content>(`/contents/${id}/`);
  }

  async createContent(data: FormData | Record<string, unknown>): Promise<Content> {
    if (data instanceof FormData) {
      const headers: HeadersInit = {};
      if (this.token) {
        headers['Authorization'] = `Token ${this.token}`;
      }
      const response = await fetch(`${API_BASE_URL}/contents/`, {
        method: 'POST',
        headers,
        body: data,
      });
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      return response.json();
    }
    return this.request<Content>('/contents/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateContent(
    id: number,
    data: Partial<Content>
  ): Promise<Content> {
    return this.request<Content>(`/contents/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteContent(id: number): Promise<void> {
    await this.request(`/contents/${id}/`, { method: 'DELETE' });
  }

  async toggleFavorite(id: number): Promise<{ is_favorite: boolean }> {
    return this.request(`/contents/${id}/favorite/`, { method: 'POST' });
  }

  async toggleArchive(id: number): Promise<{ is_archived: boolean }> {
    return this.request(`/contents/${id}/archive/`, { method: 'POST' });
  }

  async reprocessContent(id: number): Promise<{ status: string }> {
    return this.request(`/contents/${id}/reprocess/`, { method: 'POST' });
  }

  async getContentStats(): Promise<Stats> {
    return this.request<Stats>('/contents/stats/');
  }

  async bulkImport(data: BulkImportRequest): Promise<BulkImportResponse> {
    return this.request<BulkImportResponse>('/contents/bulk_import/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Search
  async search(params: SearchParams): Promise<PaginatedResponse<ContentListItem>> {
    const searchParams = new URLSearchParams();
    searchParams.set('q', params.q);
    if (params.content_type) searchParams.set('content_type', params.content_type);
    if (params.platform) searchParams.set('platform', params.platform);
    if (params.tags) params.tags.forEach((t) => searchParams.append('tags', t));
    if (params.collection) searchParams.set('collection', String(params.collection));
    if (params.favorites_only) searchParams.set('favorites_only', 'true');
    if (params.include_archived) searchParams.set('include_archived', 'true');
    if (params.semantic) searchParams.set('semantic', 'true');

    return this.request<PaginatedResponse<ContentListItem>>(
      `/search/?${searchParams.toString()}`
    );
  }

  async getSearchSuggestions(): Promise<{ suggestions: string[] }> {
    return this.request('/search/suggestions/');
  }

  async getSearchHistory(): Promise<SearchHistory[]> {
    return this.request<SearchHistory[]>('/search/history/');
  }

  async clearSearchHistory(): Promise<{ deleted: number }> {
    return this.request('/search/clear_history/', { method: 'DELETE' });
  }

  // Auth
  async login(username: string, password: string): Promise<{ token: string }> {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/api/auth/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
      throw new Error('Login failed');
    }
    const data = await response.json();
    this.setToken(data.token);
    return data;
  }
}

export const api = new ApiClient();
export default api;
