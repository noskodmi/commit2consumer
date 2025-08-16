#!/usr/bin/env python3
import asyncio
import sys
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.benchmark_service import BenchmarkService

async def main():
    if len(sys.argv) < 2:
        print("Usage: python run_benchmark.py <repository_url> [repository_name]")
        sys.exit(1)
    
    repository_url = sys.argv[1]
    repository_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    benchmark_service = BenchmarkService()
    
    repo_config = {
        'name': repository_name or 'CLI_Benchmark',
        'url': repository_url,
        'description': 'CLI benchmark run',
        'expected_features': [],
        'test_questions': [
            'What is this repository about?',
            'How do I set up this project?',
            'What are the main features?'
        ]
    }
    
    print(f"Starting benchmark for: {repository_url}")
    
    try:
        results = await benchmark_service.run_comprehensive_benchmark(repo_config)
        
        print("\n" + "="*50)
        print("BENCHMARK RESULTS")
        print("="*50)
        
        print(f"Overall Score: {results.get('overall_score', 0):.2f}")
        
        if 'processing' in results:
            p = results['processing']
            print(f"\nProcessing:")
            print(f"  Duration: {p.get('duration', 0):.2f}s")
            print(f"  Files: {p.get('metrics', {}).get('files_processed', 0)}")
        
        if 'chat' in results:
            c = results['chat']
            print(f"\nChat Performance:")
            print(f"  Avg Response Time: {c.get('metrics', {}).get('average_response_time', 0):.2f}s")
            print(f"  Success Rate: {c.get('metrics', {}).get('successful_responses', 0)}/{c.get('metrics', {}).get('questions_tested', 0)}")
        
        # Save detailed results
        output_file = f"benchmark_results_{repository_name or 'unknown'}_{int(asyncio.get_event_loop().time())}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"Benchmark failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
