import sys
import os
import asyncio

# Add src to path for easy testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from query_tc_unicode import get_character_attributes

async def run_queries():
    test_cases = ["數", "2A838"]
    
    for case in test_cases:
        print(f"--- Querying: {case} ---")
        try:
            attrs = await get_character_attributes(case)
            for k, v in attrs.items():
                print(f"{k}: {v}")
        except Exception as e:
            print(f"Error querying {case}: {e}")
        print()

def main():
    asyncio.run(run_queries())

if __name__ == "__main__":
    main()
