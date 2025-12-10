// Content Types
export type ContentType = 'text' | 'image' | 'video' | 'link' | 'mixed';
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Platform {
  id: number;
  name: string;
  slug: string;
  icon: string;
  base_url: string;
  is_active: boolean;
  content_count?: number;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
  color: string;
  is_auto_generated: boolean;
  content_count?: number;
  created_at: string;
}

export interface Collection {
  id: number;
  name: string;
  description: string;
  is_default: boolean;
  cover_image: string | null;
  content_count: number;
  preview_items: Array<{
    id: number;
    thumbnail: string | null;
    title: string | null;
  }>;
  created_at: string;
  updated_at: string;
}

export interface MediaDescription {
  id: number;
  description_type: 'ocr' | 'caption' | 'transcript' | 'scene' | 'meme';
  description_type_display: string;
  text: string;
  confidence: number;
  language: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Content {
  id: number;
  title: string;
  original_text: string;
  content_type: ContentType;
  platform: Platform | null;
  platform_name?: string;
  source_url: string;
  source_id: string;
  author_name: string;
  author_handle: string;
  media_file: string | null;
  thumbnail: string | null;
  media_url: string;
  ai_description: string;
  ai_summary: string;
  processing_status: ProcessingStatus;
  tags: Tag[];
  tag_names?: string[];
  collections: Collection[];
  media_descriptions: MediaDescription[];
  is_favorite: boolean;
  is_archived: boolean;
  view_count: number;
  original_created_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContentListItem {
  id: number;
  title: string;
  content_type: ContentType;
  platform_name: string | null;
  thumbnail: string | null;
  ai_summary: string;
  is_favorite: boolean;
  is_archived: boolean;
  tag_names: string[];
  processing_status: ProcessingStatus;
  created_at: string;
}

export interface SearchHistory {
  id: number;
  query: string;
  results_count: number;
  created_at: string;
}

export interface Stats {
  total: number;
  by_type: Record<ContentType, number>;
  by_platform: Record<string, number>;
  favorites: number;
  archived: number;
  pending_processing: number;
}

// API Response Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface SearchParams {
  q: string;
  content_type?: ContentType;
  platform?: string;
  tags?: string[];
  collection?: number;
  favorites_only?: boolean;
  include_archived?: boolean;
  semantic?: boolean;
}

export interface BulkImportItem {
  source_id?: string;
  title?: string;
  text?: string;
  content_type?: ContentType;
  url?: string;
  media_url?: string;
  author_name?: string;
  author_handle?: string;
}

export interface BulkImportRequest {
  platform: string;
  items: BulkImportItem[];
}

export interface BulkImportResponse {
  imported: number;
  total: number;
  skipped: number;
}
