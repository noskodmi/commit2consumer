from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.services.benchmark_service import BenchmarkService, BenchmarkRun

benchmark_router = APIRouter()

@benchmark_router.post("/benchmark/run")
async def run_benchmark(
    repository_url: str,
    background_tasks: BackgroundTasks,
    repository_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Start a benchmark run"""
    try:
        benchmark_service = BenchmarkService()
        
        # Find predefined repository config or create basic one
        repo_config = None
        for repo in benchmark_service.test_repositories:
            if repository_url in repo['url']:
                repo_config = repo
                break
        
        if not repo_config:
            repo_config = {
                'name': repository_name or 'Unknown',
                'url': repository_url,
                'description': 'Custom benchmark repository',
                'expected_features': [],
                'test_questions': [
                    'What is this repository about?',
                    'How do I use this project?',
                    'What are the main components?'
                ]
            }
        
        # Start benchmark in background
        background_tasks.add_task(
            benchmark_service.run_comprehensive_benchmark,
            repo_config
        )
        
        return {
            'message': 'Benchmark started',
            'repository': repo_config['name'],
            'status': 'running'
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@benchmark_router.get("/benchmark/runs")
async def list_benchmark_runs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List benchmark runs"""
    runs = db.query(BenchmarkRun).offset(skip).limit(limit).all()
    
    return {
        'runs': [
            {
                'id': run.id,
                'name': run.name,
                'repository_url': run.repository_url,
                'status': run.status,
                'started_at': run.started_at,
                'completed_at': run.completed_at,
                'overall_score': run.metrics.get('overall_quality_score') if run.metrics else None
            }
            for run in runs
        ]
    }

@benchmark_router.get("/benchmark/runs/{run_id}")
async def get_benchmark_run(run_id: int, db: Session = Depends(get_db)):
    """Get detailed benchmark results"""
    run = db.query(BenchmarkRun).filter(BenchmarkRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Benchmark run not found")
    
    return {
        'id': run.id,
        'name': run.name,
        'description': run.description,
        'repository_url': run.repository_url,
        'status': run.status,
        'started_at': run.started_at,
        'completed_at': run.completed_at,
        'results': run.results,
        'metrics': run.metrics,
        'error_message': run.error_message
    }

@benchmark_router.get("/benchmark/metrics")
async def get_benchmark_metrics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get aggregated benchmark metrics"""
    since = datetime.utcnow() - timedelta(days=days)
    
    runs = db.query(BenchmarkRun).filter(
        BenchmarkRun.started_at >= since,
        BenchmarkRun.status == "completed"
    ).all()
    
    if not runs:
        return {'message': 'No completed benchmark runs found'}
    
    # Aggregate metrics
    total_runs = len(runs)
    avg_processing_time = sum(r.metrics.get('processing_time', 0) for r in runs if r.metrics) / total_runs
    avg_quality_score = sum(r.metrics.get('overall_quality_score', 0) for r in runs if r.metrics) / total_runs
    avg_response_time = sum(r.metrics.get('avg_response_time', 0) for r in runs if r.metrics) / total_runs
    
    success_rate = len([r for r in runs if r.status == "completed"]) / len(runs) if runs else 0
    
    return {
        'period_days': days,
        'total_runs': total_runs,
        'success_rate': success_rate,
        'average_processing_time': avg_processing_time,
        'average_quality_score': avg_quality_score,
        'average_response_time': avg_response_time,
        'trend_data': [
            {
                'date': run.completed_at.isoformat() if run.completed_at else None,
                'quality_score': run.metrics.get('overall_quality_score', 0) if run.metrics else 0,
                'processing_time': run.metrics.get('processing_time', 0) if run.metrics else 0
            }
            for run in runs[-10:]  # Last 10 runs for trend
        ]
    }

@benchmark_router.get("/benchmark/compare")
async def compare_benchmarks(
    run_ids: str,  # Comma-separated list of run IDs
    db: Session = Depends(get_db)
):
    """Compare multiple benchmark runs"""
    try:
        ids = [int(id.strip()) for id in run_ids.split(',')]
        runs = db.query(BenchmarkRun).filter(BenchmarkRun.id.in_(ids)).all()
        
        if not runs:
            raise HTTPException(status_code=404, detail="No benchmark runs found")
        
        comparison = {
            'runs': [],
            'metrics_comparison': {}
        }
        
        for run in runs:
            comparison['runs'].append({
                'id': run.id,
                'name': run.name,
                'repository_url': run.repository_url,
                'completed_at': run.completed_at,
                'metrics': run.metrics
            })
        
        # Compare key metrics
        metric_keys = ['processing_time', 'avg_response_time', 'overall_quality_score']
        for key in metric_keys:
            values = [r.metrics.get(key, 0) for r in runs if r.metrics]
            if values:
                comparison['metrics_comparison'][key] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'values': values
                }
        
        return comparison
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run IDs format")