'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import type { Platform, Tag, Collection } from '@/types';
import { api } from '@/lib/api';

interface SidebarProps {
  isOpen: boolean;
}

export function Sidebar({ isOpen }: SidebarProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [platformsData, tagsData, collectionsData] = await Promise.all([
          api.getPlatforms(),
          api.getPopularTags(),
          api.getCollections(),
        ]);
        setPlatforms(platformsData);
        setTags(tagsData);
        setCollections(collectionsData);
      } catch (error) {
        console.error('Failed to fetch sidebar data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const isActive = (href: string) => {
    const url = new URL(href, 'http://localhost');
    if (pathname !== url.pathname) return false;
    for (const [key, value] of url.searchParams.entries()) {
      if (searchParams.get(key) !== value) return false;
    }
    return true;
  };

  if (!isOpen) return null;

  return (
    <aside className="w-64 bg-white h-[calc(100vh-4rem)] fixed border-r border-gray-200 overflow-y-auto">
      <div className="p-4">
        {/* Quick Filters */}
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Quick Filters
          </h3>
          <nav className="space-y-1">
            <Link
              href="/"
              className={`flex items-center px-3 py-2 rounded-lg transition-colors ${
                isActive('/') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              All Content
            </Link>
            <Link
              href="/?favorites=true"
              className={`flex items-center px-3 py-2 rounded-lg transition-colors ${
                isActive('/?favorites=true') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <svg className="w-5 h-5 mr-3 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
              Favorites
            </Link>
            <Link
              href="/?type=image"
              className={`flex items-center px-3 py-2 rounded-lg transition-colors ${
                isActive('/?type=image') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <svg className="w-5 h-5 mr-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Images
            </Link>
            <Link
              href="/?type=video"
              className={`flex items-center px-3 py-2 rounded-lg transition-colors ${
                isActive('/?type=video') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <svg className="w-5 h-5 mr-3 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Videos
            </Link>
          </nav>
        </div>

        {/* Platforms */}
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Platforms
          </h3>
          <nav className="space-y-1">
            {loading ? (
              <>
                <div className="h-8 bg-gray-100 rounded animate-pulse mb-2" />
                <div className="h-8 bg-gray-100 rounded animate-pulse mb-2" />
                <div className="h-8 bg-gray-100 rounded animate-pulse" />
              </>
            ) : (
              platforms.map((platform) => (
                <Link
                  key={platform.slug}
                  href={`/?platform=${platform.slug}`}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${
                    searchParams.get('platform') === platform.slug
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span>{platform.name}</span>
                  {platform.content_count !== undefined && (
                    <span className="text-xs text-gray-400">{platform.content_count}</span>
                  )}
                </Link>
              ))
            )}
          </nav>
        </div>

        {/* Collections */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Collections
            </h3>
            <button className="text-indigo-600 hover:text-indigo-700">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <nav className="space-y-1">
            {loading ? (
              <>
                <div className="h-8 bg-gray-100 rounded animate-pulse mb-2" />
                <div className="h-8 bg-gray-100 rounded animate-pulse" />
              </>
            ) : collections.length > 0 ? (
              collections.map((collection) => (
                <Link
                  key={collection.id}
                  href={`/?collection=${collection.id}`}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${
                    searchParams.get('collection') === String(collection.id)
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span className="truncate">{collection.name}</span>
                  <span className="text-xs text-gray-400">{collection.content_count}</span>
                </Link>
              ))
            ) : (
              <p className="text-sm text-gray-500 px-3">No collections yet</p>
            )}
          </nav>
        </div>

        {/* Tags */}
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Popular Tags
          </h3>
          <div className="flex flex-wrap gap-2">
            {loading ? (
              <>
                <div className="h-6 w-16 bg-gray-100 rounded-full animate-pulse" />
                <div className="h-6 w-20 bg-gray-100 rounded-full animate-pulse" />
                <div className="h-6 w-14 bg-gray-100 rounded-full animate-pulse" />
              </>
            ) : (
              tags.map((tag) => (
                <Link
                  key={tag.slug}
                  href={`/?tags=${tag.slug}`}
                  className="px-3 py-1 text-sm rounded-full transition-colors"
                  style={{
                    backgroundColor: `${tag.color}20`,
                    color: tag.color,
                  }}
                >
                  {tag.name}
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
