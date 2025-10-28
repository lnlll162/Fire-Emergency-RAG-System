interface CacheEntry<T> {
  data: T
  timestamp: number
}

class Cache {
  private cache: Map<string, CacheEntry<unknown>> = new Map()
  private ttl: number = 5 * 60 * 1000 // 5分钟默认过期时间

  set<T>(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  get<T>(key: string, ttl?: number): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    const maxAge = ttl || this.ttl
    if (Date.now() - entry.timestamp > maxAge) {
      this.cache.delete(key)
      return null
    }

    return entry.data as T
  }

  has(key: string, ttl?: number): boolean {
    return this.get(key, ttl) !== null
  }

  delete(key: string): void {
    this.cache.delete(key)
  }

  clear(): void {
    this.cache.clear()
  }

  size(): number {
    return this.cache.size
  }
}

export const apiCache = new Cache()

