from multi_method_search import MultiMethodSearch

def test():
    searcher = MultiMethodSearch()
    
    try:
        # Test the multi-method search
        print("Testing multi-method search for 'oil'...")
        results = searcher.multi_method_search(
            query="oil",
            countries=None,
            supplier_types=None,
            use_ai_analysis=False,  # Skip AI for now
            limit=5
        )
        
        print(f"Success: {results.get('success')}")
        print(f"Total found: {results.get('total_found')}")
        print(f"Final count: {results.get('final_count')}")
        
        if results.get('suppliers'):
            print(f"\nFirst supplier:")
            supplier = results['suppliers'][0]
            for key, value in supplier.items():
                if key != 'products':  # Skip long products text
                    print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        searcher.close()

if __name__ == "__main__":
    test()