'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Sidebar, SearchBar, StatsCards, ContentCard } from '@/components';
import type { ContentListItem, PaginatedResponse } from '@/types';
import { api } from '@/lib/api';

function HomeContent() {
  const searchParams = useSearchParams();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [contents, setContents] = useState<ContentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchContents = async (pageNum: number, append = false) => {
    setLoading(true);
    try {
      const params: Record<string, string | boolean | number | string[]> = { page: pageNum };

      const type = searchParams.get('type');
      const platform = searchParams.get('platform');
      const collection = searchParams.get('collection');
      const favorites = searchParams.get('favorites');
      const tags = searchParams.getAll('tags');

      if (type) params.type = type;
      if (platform) params.platform = platform;
      if (collection) params.collection = parseInt(collection);
      if (favorites === 'true') params.favorites = true;
      if (tags.length > 0) params.tags = tags;

      const data: PaginatedResponse<ContentListItem> = await api.getContents(params as Parameters<typeof api.getContents>[0]);

      if (append) {
        setContents(prev => [...prev, ...data.results]);
      } else {
        setContents(data.results);
      }
      setHasMore(!!data.next);
    } catch (error) {
      console.error('Failed to fetch contents:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    fetchContents(1, false);
  }, [searchParams]);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchContents(nextPage, true);
  };

  const handleFavoriteToggle = (id: number, isFavorite: boolean) => {
    setContents(prev =>
      prev.map(c => (c.id === id ? { ...c, is_favorite: isFavorite } : c))
    );
  };

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200 fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-md hover:bg-gray-100"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <a href="/" className="ml-4 text-xl font-bold text-indigo-600">
                Content Aggregator
              </a>
            </div>

            <SearchBar />

            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-full hover:bg-gray-100" title="Add Content">
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white font-medium">
                U
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex pt-16">
        <Sidebar isOpen={sidebarOpen} />

        <main className={`flex-1 p-6 transition-all duration-200 ${sidebarOpen ? 'ml-64' : 'ml-0'}`}>
          <div className="max-w-6xl mx-auto">
            <StatsCards />

            {/* Content Header */}
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {searchParams.get('favorites') === 'true'
                  ? 'Favorites'
                  : searchParams.get('type')
                  ? `${searchParams.get('type')?.charAt(0).toUpperCase()}${searchParams.get('type')?.slice(1)}s`
                  : searchParams.get('platform')
                  ? `From ${searchParams.get('platform')}`
                  : 'Recent Content'}
              </h2>
              <div className="flex items-center space-x-2">
                <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
                  <option value="">Sort by Date</option>
                  <option value="view_count">Sort by Views</option>
                </select>
              </div>
            </div>

            {/* Content Grid */}
            {loading && contents.length === 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden animate-pulse">
                    <div className="h-48 bg-gray-200" />
                    <div className="p-4">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                      <div className="h-3 bg-gray-200 rounded w-full mb-2" />
                      <div className="h-3 bg-gray-200 rounded w-2/3" />
                    </div>
                  </div>
                ))}
              </div>
            ) : contents.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {contents.map((content) => (
                    <ContentCard
                      key={content.id}
                      content={content}
                      onFavoriteToggle={handleFavoriteToggle}
                    />
                  ))}
                </div>

                {hasMore && (
                  <div className="mt-8 text-center">
                    <button
                      onClick={loadMore}
                      disabled={loading}
                      className="px-6 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium disabled:opacity-50"
                    >
                      {loading ? 'Loading...' : 'Load More'}
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-24 w-24 text-gray-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">No content yet</h3>
                <p className="mt-2 text-gray-500">
                  Start collecting content from your favorite platforms!
                </p>
                <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                  Add Your First Content
                </button>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <HomeContent />
    </Suspense>
  );
}
