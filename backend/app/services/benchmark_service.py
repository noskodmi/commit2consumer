import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

from app.core.database import Base, get_db
from app.services.github_service import GitHubService
from app.services.vector_service import VectorService
from app.services.rag_service import RAGService
from app.services.documentation_generator import DocumentationGenerator

logger = logging.getLogger(__name__)

# Benchmark Models
class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    repository_url = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String, default="running")  # running, completed, failed
    results = Column(JSON)
    metrics = Column(JSON)
    error_message = Column(Text)

class BenchmarkTest(Base):
    __tablename__ = "benchmark_tests"
    
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, nullable=False)
    test_name = Column(String, nullable=False)
    test_type = Column(String, nullable=False)  # processing, retrieval, generation, accuracy
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration = Column(Float)  # seconds
    success = Column(String, default=True)
    metrics = Column(JSON)
    error_message = Column(Text)

class BenchmarkService:
    def __init__(self):
        self.github_service = GitHubService()
        self.vector_service = VectorService()
        self.rag_service = RAGService()
        self.doc_generator = DocumentationGenerator()
        
        # Predefined test repositories for benchmarking
        self.test_repositories = [
            {
                "name": "FastAPI",
                "url": "https://github.com/tiangolo/fastapi",
                "description": "Modern, fast Python web framework",
                "expected_features": ["REST API", "async/await", "type hints", "documentation"],
                "test_questions": [
                    "How do I create a FastAPI application?",
                    "What is dependency injection in FastAPI?",
                    "How do I handle authentication?",
                    "How do I add middleware?",
                    "What are path parameters?"
                ]
            },
            {
                "name": "React",
                "url": "https://github.com/facebook/react",
                "description": "JavaScript library for building user interfaces",
                "expected_features": ["components", "hooks", "JSX", "virtual DOM"],
                "test_questions": [
                    "What is a React component?",
                    "How do I use useState hook?",
                    "What is JSX?",
                    "How do I handle events in React?",
                    "What is the virtual DOM?"
                ]
            },
            {
                "name": "Express.js",
                "url": "https://github.com/expressjs/express",
                "description": "Fast, unopinionated web framework for Node.js",
                "expected_features": ["routing", "middleware", "HTTP server"],
                "test_questions": [
                    "How do I create an Express server?",
                    "What is middleware in Express?",
                    "How do I handle routes?",
                    "How do I serve static files?",
                    "How do I handle errors?"
                ]
            }
        ]
    
    async def run_comprehensive_benchmark(self, repository_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a comprehensive benchmark on a repository"""
        
        benchmark_run = BenchmarkRun(
            name=f"Benchmark_{repository_config['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"Comprehensive benchmark for {repository_config['name']}",
            repository_url=repository_config['url']
        )
        
        # Save benchmark run (in a real app, you'd use a database session)
        logger.info(f"Starting benchmark run: {benchmark_run.name}")
        
        try:
            results = {}
            
            # 1. Repository Processing Benchmark
            processing_metrics = await self._benchmark_repository_processing(
                repository_config, benchmark_run.id
            )
            results['processing'] = processing_metrics
            
            # 2. Vector Search Benchmark
            search_metrics = await self._benchmark_vector_search(
                repository_config, benchmark_run.id
            )
            results['search'] = search_metrics
            
            # 3. Documentation Generation Benchmark
            doc_metrics = await self._benchmark_documentation_generation(
                repository_config, benchmark_run.id
            )
            results['documentation'] = doc_metrics
            
            # 4. RAG Chat Benchmark
            chat_metrics = await self._benchmark_rag_chat(
                repository_config, benchmark_run.id
            )
            results['chat'] = chat_metrics
            
            # 5. Overall Quality Assessment
            quality_metrics = await self._benchmark_quality_assessment(
                repository_config, results
            )
            results['quality'] = quality_metrics
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(results)
            results['overall_score'] = overall_score
            
            benchmark_run.status = "completed"
            benchmark_run.completed_at = datetime.utcnow()
            benchmark_run.results = results
            benchmark_run.metrics = self._extract_key_metrics(results)
            
            logger.info(f"Benchmark completed: {benchmark_run.name}, Score: {overall_score}")
            return results
            
        except Exception as e:
            logger.error(f"Benchmark failed: {str(e)}")
            benchmark_run.status = "failed"
            benchmark_run.error_message = str(e)
            benchmark_run.completed_at = datetime.utcnow()
            raise
    
    async def _benchmark_repository_processing(self, repo_config: Dict, run_id: int) -> Dict[str, Any]:
        """Benchmark repository processing speed and accuracy"""
        
        test = BenchmarkTest(
            run_id=run_id,
            test_name="repository_processing",
            test_type="processing"
        )
        
        start_time = time.time()
        
        try:
            # Validate repository
            repo_info = await self.github_service.validate_repository(repo_config['url'])
            
            # Process repository
            import tempfile
            import shutil
            temp_dir = tempfile.mkdtemp()
            
            try:
                cloned_path = await self.github_service.clone_repository(repo_config['url'], temp_dir)
                files_data = await self.github_service.process_repository(cloned_path)
                
                # Create vector collection
                collection_name = f"benchmark_{repo_config['name'].lower()}_{int(time.time())}"
                await self.vector_service.create_collection(collection_name)
                vector_ids = await self.vector_service.add_documents(collection_name, files_data)
                
                end_time = time.time()
                duration = end_time - start_time
                
                metrics = {
                    'duration_seconds': duration,
                    'files_processed': len(files_data),
                    'total_size_bytes': sum(f['size'] for f in files_data),
                    'vectors_created': len(vector_ids),
                    'processing_rate_files_per_second': len(files_data) / duration,
                    'languages_detected': list(set(f['language'] for f in files_data)),
                    'average_file_size': sum(f['size'] for f in files_data) / len(files_data) if files_data else 0
                }
                
                test.success = True
                test.duration = duration
                test.metrics = metrics
                test.completed_at = datetime.utcnow()
                
                return {
                    'success': True,
                    'duration': duration,
                    'metrics': metrics,
                    'collection_name': collection_name
                }
                
            finally:
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            end_time = time.time()
            test.success = False
            test.duration = end_time - start_time
            test.error_message = str(e)
            test.completed_at = datetime.utcnow()
            raise
    
    async def _benchmark_vector_search(self, repo_config: Dict, run_id: int) -> Dict[str, Any]:
        """Benchmark vector search performance and accuracy"""
        
        test = BenchmarkTest(
            run_id=run_id,
            test_name="vector_search",
            test_type="retrieval"
        )
        
        start_time = time.time()
        
        try:
            collection_name = f"benchmark_{repo_config['name'].lower()}_{int(time.time())}"
            
            # Test search queries
            test_queries = [
                "main function",
                "class definition", 
                "API endpoint",
                "error handling",
                "configuration"
            ]
            
            search_results = []
            search_times = []
            
            for query in test_queries:
                query_start = time.time()
                results = await self.vector_service.search_similar(
                    collection_name=collection_name,
                    query=query,
                    n_results=5
                )
                query_end = time.time()
                
                search_times.append(query_end - query_start)
                search_results.append({
                    'query': query,
                    'results_count': len(results),
                    'duration': query_end - query_start,
                    'top_relevance': results[0]['distance'] if results else 1.0
                })
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            metrics = {
                'total_duration': total_duration,
                'queries_tested': len(test_queries),
                'average_query_time': sum(search_times) / len(search_times),
                'max_query_time': max(search_times),
                'min_query_time': min(search_times),
                'search_results': search_results
            }
            
            test.success = True
            test.duration = total_duration
            test.metrics = metrics
            test.completed_at = datetime.utcnow()
            
            return {
                'success': True,
                'duration': total_duration,
                'metrics': metrics
            }
            
        except Exception as e:
            end_time = time.time()
            test.success = False
            test.duration = end_time - start_time
            test.error_message = str(e)
            test.completed_at = datetime.utcnow()
            raise
    
    async def _benchmark_documentation_generation(self, repo_config: Dict, run_id: int) -> Dict[str, Any]:
        """Benchmark documentation generation quality and speed"""
        
        test = BenchmarkTest(
            run_id=run_id,
            test_name="documentation_generation",
            test_type="generation"
        )
        
        start_time = time.time()
        
        try:
            # Mock repository data for documentation generation
            repository_data = {
                'name': repo_config['name'],
                'description': repo_config['description'],
                'language': 'python',  # simplified for benchmark
                'files': []  # would be populated from actual processing
            }
            
            # Generate documentation
            doc_start = time.time()
            documentation = await self.doc_generator.generate_documentation(repository_data)
            doc_end = time.time()
            
            # Generate FAQ
            faq_start = time.time()
            faq = await self.doc_generator.generate_faq(repository_data)
            faq_end = time.time()
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Quality assessment
            doc_quality = self._assess_documentation_quality(documentation, repo_config)
            faq_quality = self._assess_faq_quality(faq, repo_config)
            
            metrics = {
                'total_duration': total_duration,
                'documentation_generation_time': doc_end - doc_start,
                'faq_generation_time': faq_end - faq_start,
                'documentation_sections': len(documentation),
                'faq_items': len(faq),
                'documentation_quality_score': doc_quality,
                'faq_quality_score': faq_quality,
                'total_content_length': sum(len(str(v)) for v in documentation.values()) + sum(len(item['answer']) for item in faq)
            }
            
            test.success = True
            test.duration = total_duration
            test.metrics = metrics
            test.completed_at = datetime.utcnow()
            
            return {
                'success': True,
                'duration': total_duration,
                'metrics': metrics,
                'documentation': documentation,
                'faq': faq
            }
            
        except Exception as e:
            end_time = time.time()
            test.success = False
            test.duration = end_time - start_time
            test.error_message = str(e)
            test.completed_at = datetime.utcnow()
            raise
    
    async def _benchmark_rag_chat(self, repo_config: Dict, run_id: int) -> Dict[str, Any]:
        """Benchmark RAG chat performance and accuracy"""
        
        test = BenchmarkTest(
            run_id=run_id,
            test_name="rag_chat",
            test_type="generation"
        )
        
        start_time = time.time()
        
        try:
            collection_name = f"benchmark_{repo_config['name'].lower()}_{int(time.time())}"
            test_questions = repo_config.get('test_questions', [])
            
            chat_results = []
            response_times = []
            
            repository_info = {
                'name': repo_config['name'],
                'description': repo_config['description'],
                'language': 'python'
            }
            
            for question in test_questions:
                question_start = time.time()
                
                try:
                    response = await self.rag_service.answer_question(
                        collection_name=collection_name,
                        question=question,
                        repository_info=repository_info
                    )
                    
                    question_end = time.time()
                    question_duration = question_end - question_start
                    response_times.append(question_duration)
                    
                    # Assess answer quality
                    quality_score = self._assess_answer_quality(question, response['answer'], repo_config)
                    
                    chat_results.append({
                        'question': question,
                        'answer': response['answer'][:200] + "...",  # truncated for storage
                        'duration': question_duration,
                        'context_chunks': len(response.get('context_used', [])),
                        'quality_score': quality_score
                    })
                    
                except Exception as e:
                    question_end = time.time()
                    question_duration = question_end - question_start
                    response_times.append(question_duration)
                    
                    chat_results.append({
                        'question': question,
                        'answer': f"ERROR: {str(e)}",
                        'duration': question_duration,
                        'context_chunks': 0,
                        'quality_score': 0.0,
                        'error': True
                    })
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            successful_responses = [r for r in chat_results if not r.get('error', False)]
            average_quality = sum(r['quality_score'] for r in successful_responses) / len(successful_responses) if successful_responses else 0
            
            metrics = {
                'total_duration': total_duration,
                'questions_tested': len(test_questions),
                'successful_responses': len(successful_responses),
                'failed_responses': len(chat_results) - len(successful_responses),
                'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0,
                'min_response_time': min(response_times) if response_times else 0,
                'average_quality_score': average_quality,
                'chat_results': chat_results
            }
            
            test.success = True
            test.duration = total_duration
            test.metrics = metrics
            test.completed_at = datetime.utcnow()
            
            return {
                'success': True,
                'duration': total_duration,
                'metrics': metrics
            }
            
        except Exception as e:
            end_time = time.time()
            test.success = False
            test.duration = end_time - start_time
            test.error_message = str(e)
            test.completed_at = datetime.utcnow()
            raise
    
    async def _benchmark_quality_assessment(self, repo_config: Dict, results: Dict) -> Dict[str, Any]:
        """Assess overall system quality"""
        
        quality_metrics = {
            'processing_efficiency': 0.0,
            'search_accuracy': 0.0,
            'documentation_completeness': 0.0,
            'chat_helpfulness': 0.0,
            'overall_quality': 0.0
        }
        
        try:
            # Processing efficiency (based on speed and success)
            if results.get('processing', {}).get('success'):
                processing_time = results['processing']['duration']
                files_count = results['processing']['metrics']['files_processed']
                # Normalize score (good performance = higher score)
                efficiency = min(1.0, (files_count / processing_time) / 10)  # Assuming 10 files/sec is excellent
                quality_metrics['processing_efficiency'] = efficiency
            
            # Search accuracy (based on relevance scores)
            if results.get('search', {}).get('success'):
                search_results = results['search']['metrics']['search_results']
                if search_results:
                    avg_relevance = 1.0 - sum(r.get('top_relevance', 1.0) for r in search_results) / len(search_results)
                    quality_metrics['search_accuracy'] = max(0.0, avg_relevance)
            
            # Documentation completeness
            if results.get('documentation', {}).get('success'):
                doc_quality = results['documentation']['metrics'].get('documentation_quality_score', 0.0)
                faq_quality = results['documentation']['metrics'].get('faq_quality_score', 0.0)
                quality_metrics['documentation_completeness'] = (doc_quality + faq_quality) / 2
            
            # Chat helpfulness
            if results.get('chat', {}).get('success'):
                avg_quality = results['chat']['metrics'].get('average_quality_score', 0.0)
                success_rate = results['chat']['metrics'].get('successful_responses', 0) / max(1, results['chat']['metrics'].get('questions_tested', 1))
                quality_metrics['chat_helpfulness'] = (avg_quality + success_rate) / 2
            
            # Overall quality (weighted average)
            weights = {
                'processing_efficiency': 0.2,
                'search_accuracy': 0.3,
                'documentation_completeness': 0.2,
                'chat_helpfulness': 0.3
            }
            
            overall = sum(quality_metrics[key] * weights[key] for key in weights)
            quality_metrics['overall_quality'] = overall
            
        except Exception as e:
            logger.error(f"Quality assessment error: {str(e)}")
        
        return quality_metrics
    
    def _assess_documentation_quality(self, documentation: Dict, repo_config: Dict) -> float:
        """Assess quality of generated documentation"""
        score = 0.0
        max_score = 0.0
        
        # Check for required sections
        required_sections = ['overview', 'setup_guide', 'api_documentation', 'architecture']
        for section in required_sections:
            max_score += 1.0
            if section in documentation and documentation[section]:
                content_length = len(documentation[section])
                if content_length > 100:  # Minimum meaningful content
                    score += 1.0
                elif content_length > 50:
                    score += 0.5
        
        # Check for expected features mentioned
        expected_features = repo_config.get('expected_features', [])
        if expected_features:
            all_content = ' '.join(str(v).lower() for v in documentation.values())
            for feature in expected_features:
                max_score += 0.5
                if feature.lower() in all_content:
                    score += 0.5
        
        return score / max_score if max_score > 0 else 0.0
    
    def _assess_faq_quality(self, faq: List[Dict], repo_config: Dict) -> float:
        """Assess quality of generated FAQ"""
        if not faq:
            return 0.0
        
        score = 0.0
        max_score = len(faq)
        
        for item in faq:
            if 'question' in item and 'answer' in item:
                question_length = len(item['question'])
                answer_length = len(item['answer'])
                
                if question_length > 10 and answer_length > 50:
                    score += 1.0
                elif question_length > 5 and answer_length > 20:
                    score += 0.5
        
        return score / max_score
    
    def _assess_answer_quality(self, question: str, answer: str, repo_config: Dict) -> float:
        """Assess quality of RAG chat answer"""
        score = 0.0
        
        # Basic checks
        if len(answer) > 50:
            score += 0.3
        if len(answer) > 200:
            score += 0.2
        
        # Check if answer is relevant (simple keyword matching)
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        common_words = question_words.intersection(answer_words)
        
        if len(common_words) > 0:
            score += 0.2
        if len(common_words) > 2:
            score += 0.1
        
        # Check for expected features
        expected_features = repo_config.get('expected_features', [])
        for feature in expected_features:
            if feature.lower() in answer.lower():
                score += 0.1
        
        # Check if answer seems helpful (not just error or "I don't know")
        if not any(phrase in answer.lower() for phrase in ["i don't know", "cannot", "unable", "error"]):
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """Calculate overall benchmark score"""
        weights = {
            'processing': 0.25,
            'search': 0.25,
            'documentation': 0.25,
            'chat': 0.25
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for component, weight in weights.items():
            if component in results and results[component].get('success'):
                if component == 'quality':
                    component_score = results[component]['overall_quality']
                else:
                    # Calculate component score based on success and performance
                    duration = results[component].get('duration', float('inf'))
                    # Normalize duration score (lower is better)
                    duration_score = max(0.0, 1.0 - (duration / 300))  # 5 minutes max
                    component_score = duration_score
                
                total_score += component_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _extract_key_metrics(self, results: Dict) -> Dict[str, Any]:
        """Extract key metrics for tracking"""
        metrics = {}
        
        if 'processing' in results:
            p = results['processing']
            if p.get('success'):
                metrics.update({
                    'processing_time': p['duration'],
                    'files_processed': p['metrics']['files_processed'],
                    'processing_rate': p['metrics']['processing_rate_files_per_second']
                })
        
        if 'search' in results:
            s = results['search']
            if s.get('success'):
                metrics.update({
                    'avg_search_time': s['metrics']['average_query_time'],
                    'max_search_time': s['metrics']['max_query_time']
                })
        
        if 'chat' in results:
            c = results['chat']
            if c.get('success'):
                metrics.update({
                    'avg_response_time': c['metrics']['average_response_time'],
                    'chat_success_rate': c['metrics']['successful_responses'] / max(1, c['metrics']['questions_tested']),
                    'avg_chat_quality': c['metrics']['average_quality_score']
                })
        
        if 'quality' in results:
            metrics.update({
                'overall_quality_score': results['quality']['overall_quality']
            })
        
        return metrics