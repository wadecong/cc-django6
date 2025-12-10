'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import type { Content } from '@/types';
import { api } from '@/lib/api';

export default function ContentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const [content, setContent] = useState<Content | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const data = await api.getContent(id);
        setContent(data);
      } catch (err) {
        setError('Failed to load content');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchContent();
    }
  }, [id]);

  const handleFavorite = async () => {
    if (!content) return;
    try {
      const result = await api.toggleFavorite(content.id);
      setContent({ ...content, is_favorite: result.is_favorite });
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const handleArchive = async () => {
    if (!content) return;
    try {
      const result = await api.toggleArchive(content.id);
      setContent({ ...content, is_archived: result.is_archived });
    } catch (err) {
      console.error('Failed to toggle archive:', err);
    }
  };

  const handleReprocess = async () => {
    if (!content) return;
    try {
      await api.reprocessContent(content.id);
      setContent({ ...content, processing_status: 'processing' });
    } catch (err) {
      console.error('Failed to reprocess:', err);
    }
  };

  const handleDelete = async () => {
    if (!content || !confirm('Are you sure you want to delete this content?')) return;
    try {
      await api.deleteContent(content.id);
      router.push('/');
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Content not found</h1>
          <Link href="/" className="text-indigo-600 hover:text-indigo-700">
            Go back home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button onClick={() => router.back()} className="p-2 hover:bg-gray-100 rounded-lg mr-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <Link href="/" className="text-xl font-bold text-indigo-600">
                Content Aggregator
              </Link>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleFavorite}
                className={`p-2 rounded-lg ${content.is_favorite ? 'bg-yellow-100' : 'hover:bg-gray-100'}`}
                title="Toggle Favorite"
              >
                <svg
                  className={`w-6 h-6 ${content.is_favorite ? 'text-yellow-500' : 'text-gray-400'}`}
                  fill={content.is_favorite ? 'currentColor' : 'none'}
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </button>
              <button
                onClick={handleArchive}
                className={`p-2 rounded-lg ${content.is_archived ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
                title="Toggle Archive"
              >
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </button>
              <button onClick={handleDelete} className="p-2 rounded-lg hover:bg-red-100" title="Delete">
                <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Media */}
            {(content.thumbnail || content.media_file || content.media_url) && (
              <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-6">
                {content.content_type === 'video' ? (
                  <video
                    src={content.media_file || content.media_url}
                    controls
                    className="w-full"
                    poster={content.thumbnail || undefined}
                  />
                ) : (
                  <img
                    src={content.thumbnail || content.media_file || content.media_url}
                    alt={content.title}
                    className="w-full"
                  />
                )}
              </div>
            )}

            {/* Title & Content */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">
                {content.title || 'Untitled'}
              </h1>

              {content.original_text && (
                <div className="prose max-w-none mb-6">
                  <p className="text-gray-700 whitespace-pre-wrap">{content.original_text}</p>
                </div>
              )}

              {/* Source */}
              {content.source_url && (
                <a
                  href={content.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-indigo-600 hover:text-indigo-700"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  View Original
                </a>
              )}
            </div>

            {/* AI Descriptions */}
            {(content.ai_description || content.media_descriptions?.length > 0) && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  AI Analysis
                </h2>

                {content.ai_summary && (
                  <div className="mb-4 p-4 bg-indigo-50 rounded-lg">
                    <p className="text-sm font-medium text-indigo-900">Summary</p>
                    <p className="text-indigo-700">{content.ai_summary}</p>
                  </div>
                )}

                {content.media_descriptions?.map((desc) => (
                  <div key={desc.id} className="mb-4 last:mb-0">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        {desc.description_type_display}
                      </span>
                      <span className="text-xs text-gray-500">
                        Confidence: {Math.round(desc.confidence * 100)}%
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm whitespace-pre-wrap">{desc.text}</p>
                  </div>
                ))}

                {content.processing_status === 'processing' && (
                  <div className="flex items-center text-blue-600">
                    <svg className="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Processing...
                  </div>
                )}

                {content.processing_status === 'failed' && (
                  <button
                    onClick={handleReprocess}
                    className="text-sm text-indigo-600 hover:text-indigo-700"
                  >
                    Retry Processing
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Metadata */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Details</h3>
              <dl className="space-y-3 text-sm">
                {content.platform && (
                  <div>
                    <dt className="text-gray-500">Platform</dt>
                    <dd className="font-medium text-gray-900">{content.platform.name}</dd>
                  </div>
                )}
                {content.author_name && (
                  <div>
                    <dt className="text-gray-500">Author</dt>
                    <dd className="font-medium text-gray-900">
                      {content.author_name}
                      {content.author_handle && (
                        <span className="text-gray-500 ml-1">@{content.author_handle}</span>
                      )}
                    </dd>
                  </div>
                )}
                <div>
                  <dt className="text-gray-500">Type</dt>
                  <dd className="font-medium text-gray-900 capitalize">{content.content_type}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Views</dt>
                  <dd className="font-medium text-gray-900">{content.view_count}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Added</dt>
                  <dd className="font-medium text-gray-900">
                    {new Date(content.created_at).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Tags */}
            {content.tags?.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {content.tags.map((tag) => (
                    <Link
                      key={tag.id}
                      href={`/?tags=${tag.slug}`}
                      className="px-3 py-1 text-sm rounded-full"
                      style={{
                        backgroundColor: `${tag.color}20`,
                        color: tag.color,
                      }}
                    >
                      {tag.name}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Collections */}
            {content.collections?.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Collections</h3>
                <div className="space-y-2">
                  {content.collections.map((collection) => (
                    <Link
                      key={collection.id}
                      href={`/?collection=${collection.id}`}
                      className="block px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-700"
                    >
                      {collection.name}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
