#!/usr/bin/env python3
"""
Check Database and AI Optimization Status
"""

import psycopg2
import os
from dotenv import load_dotenv
import time

load_dotenv()

print('=' * 80)
print('DATABASE & AI OPTIMIZATION AUDIT FOR FDX.TRADING')
print('=' * 80)

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# 1. Performance Benchmarks
print('\n1. SEARCH PERFORMANCE BENCHMARKS:')
print('-' * 40)

benchmarks = [
    ('Fast cache lookup', 'SELECT COUNT(DISTINCT supplier_id) FROM supplier_search_keywords WHERE keyword = \'oil\''),
    ('Traditional search', 'SELECT COUNT(*) FROM suppliers WHERE products ILIKE \'%oil%\''),
    ('Multi-keyword cache', 'SELECT COUNT(DISTINCT supplier_id) FROM supplier_search_keywords WHERE keyword IN (\'chocolate\', \'wafer\')'),
]

for name, query in benchmarks:
    try:
        start = time.time()
        cur.execute(query)
        result = cur.fetchone()[0]
        elapsed = (time.time() - start) * 1000
        
        if elapsed < 50:
            status = 'EXCELLENT'
        elif elapsed < 100:
            status = 'GOOD'
        elif elapsed < 500:
            status = 'OK'
        else:
            status = 'SLOW'
            
        print(f'{status:10} | {elapsed:7.1f}ms | {name}')
    except Exception as e:
        print(f'ERROR      | {name}: {str(e)[:30]}')

# 2. Database Optimization Status
print('\n2. DATABASE OPTIMIZATION STATUS:')
print('-' * 40)

# Check indexes
cur.execute("""
    SELECT COUNT(*) FROM pg_indexes 
    WHERE tablename = 'suppliers'
""")
index_count = cur.fetchone()[0]
print(f'Indexes on suppliers table: {index_count}')

# Check search cache
cur.execute('SELECT COUNT(DISTINCT supplier_id) FROM supplier_search_keywords')
cached_suppliers = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM suppliers')
total_suppliers = cur.fetchone()[0]
cache_coverage = cached_suppliers * 100 // total_suppliers

print(f'Search cache coverage: {cached_suppliers:,}/{total_suppliers:,} ({cache_coverage}%)')

if cache_coverage < 50:
    print('  WARNING: Low cache coverage - need to complete keyword extraction')
elif cache_coverage < 80:
    print('  OK: Moderate cache coverage - consider expanding')
else:
    print('  EXCELLENT: Good cache coverage')

# 3. AI Enhancement Status
print('\n3. AI DATA ENHANCEMENT STATUS:')
print('-' * 40)

cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN LENGTH(products) > 200 THEN 1 END) as enhanced,
        COUNT(CASE WHEN LENGTH(products) > 500 THEN 1 END) as detailed,
        AVG(LENGTH(COALESCE(products, ''))) as avg_length
    FROM suppliers
""")
ai_stats = cur.fetchone()

print(f'Total suppliers: {ai_stats[0]:,}')
print(f'AI-enhanced (>200 chars): {ai_stats[1]:,} ({ai_stats[1]*100//ai_stats[0]}%)')
print(f'Detailed descriptions (>500 chars): {ai_stats[2]:,} ({ai_stats[2]*100//ai_stats[0]}%)')
print(f'Average description length: {ai_stats[3]:.0f} characters')

# 4. Missing Critical Optimizations
print('\n4. OPTIMIZATION CHECKLIST:')
print('-' * 40)

optimizations = {
    'Search cache table': 'supplier_search_keywords' in [row[0] for row in cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'").fetchall() or []],
    'Fast search function': 'fast_search' in [row[0] for row in cur.execute("SELECT proname FROM pg_proc WHERE proname = 'fast_search'").fetchall() or []],
    'Adequate cache coverage': cache_coverage > 50,
    'AI-enhanced descriptions': ai_stats[1] > 10000,
}

# Check each optimization
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'supplier_search_keywords'")
has_cache_table = cur.fetchone() is not None

cur.execute("SELECT proname FROM pg_proc WHERE proname = 'fast_search'")
has_search_function = cur.fetchone() is not None

print(f'Search cache table: {"YES" if has_cache_table else "NO - Run create_search_cache.py"}')
print(f'Fast search function: {"YES" if has_search_function else "NO - Run quick_search_setup.py"}')
print(f'Cache coverage > 50%: {"YES" if cache_coverage > 50 else "NO - Need to extract more keywords"}')
print(f'AI descriptions > 10K: {"YES" if ai_stats[1] > 10000 else "NO - Need AI enhancement"}')

# 5. Recommendations
print('\n' + '=' * 80)
print('OPTIMIZATION RECOMMENDATIONS')
print('=' * 80)

issues = []
if cache_coverage < 80:
    issues.append(f'Expand search cache (currently {cache_coverage}%)')
if ai_stats[1] < 15000:
    issues.append(f'Enhance more products with AI (currently {ai_stats[1]:,})')
if not has_search_function:
    issues.append('Create fast_search function')

if issues:
    print('\nTO COMPLETE OPTIMIZATION:')
    for i, issue in enumerate(issues, 1):
        print(f'{i}. {issue}')
    
    print('\nRUN THESE COMMANDS:')
    if cache_coverage < 80:
        print('python create_search_cache.py  # Complete keyword extraction')
    if not has_search_function:
        print('python quick_search_setup.py   # Create search functions')
else:
    print('\nDATABASE IS FULLY OPTIMIZED!')
    print('- All search functions ready')
    print('- Cache coverage adequate')
    print('- AI enhancements complete')

print('\n' + '=' * 80)
print('AI SEARCH READINESS')
print('=' * 80)

if ai_stats[1] > 10000 and cache_coverage > 50:
    print('STATUS: READY FOR AI-POWERED SEARCH')
    print('\nYou can now implement:')
    print('1. Semantic search using product descriptions')
    print('2. Similarity matching for "find suppliers like X"')
    print('3. Natural language queries')
    print('4. Multi-criteria scoring')
    print('\nNext step: Configure Azure OpenAI for semantic embeddings')
else:
    print('STATUS: BASIC SEARCH ONLY')
    print('\nNeed to complete:')
    if ai_stats[1] < 10000:
        print(f'- Enhance {15000 - ai_stats[1]:,} more suppliers with AI')
    if cache_coverage < 50:
        print(f'- Add {(total_suppliers * 0.8) - cached_suppliers:.0f} more suppliers to cache')

cur.close()
conn.close()