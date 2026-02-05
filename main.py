import sys
import os
import asyncio

# Add src to path for easy testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from query_tc_unicode import get_character_attributes, get_character_meaning

async def run_queries():
    test_cases = ["數", "2A838", "23A3C"]
    
    for case in test_cases:
        print(f"--- Querying: {case} ---")
        try:
            attrs = await get_character_attributes(case)
            for k, v in attrs.items():
                print(f"{k}: {v}")
            
            char = attrs.get('char')
            if char:
                print(f"Meaning of {char}:")
                meaning = await get_character_meaning(char)
                print(meaning)
            else:
                # If char not in attributes, it might be a hex string for an obscure character
                # Let's try to convert hex to char if possible
                if len(case) > 1:
                     try:
                         c = chr(int(case, 16))
                         print(f"Meaning of {c}:")
                         meaning = await get_character_meaning(c)
                         print(meaning)
                     except:
                         pass
        except Exception as e:
            print(f"Error querying {case}: {e}")
        print()

    # Specific test for '舡'
    print("--- Querying Meaning: 舡 ---")
    try:
        meaning = await get_character_meaning("舡")
        print(f"Meaning: {meaning}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    asyncio.run(run_queries())

if __name__ == "__main__":
    main()
