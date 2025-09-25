"""
Performance monitoring and metrics collection for the Agentic POC
"""
import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, success: bool = True, error: Optional[str] = None):
        """Mark the operation as complete"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'operation': self.operation,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'success': self.success,
            'error': self.error,
            'metadata': self.metadata,
            'timestamp': datetime.fromtimestamp(self.start_time).isoformat()
        }


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics: list[PerformanceMetrics] = []
        self.logger = logging.getLogger(__name__)
    
    def start_operation(self, operation: str, metadata: Optional[Dict[str, Any]] = None) -> PerformanceMetrics:
        """Start tracking an operation"""
        metrics = PerformanceMetrics(
            operation=operation,
            start_time=time.time(),
            metadata=metadata or {}
        )
        self.metrics.append(metrics)
        self.logger.debug(f"Started operation: {operation}")
        return metrics
    
    def complete_operation(self, metrics: PerformanceMetrics, success: bool = True, error: Optional[str] = None):
        """Complete an operation"""
        metrics.complete(success=success, error=error)
        
        log_level = logging.INFO if success else logging.WARNING
        self.logger.log(
            log_level,
            f"Completed operation: {metrics.operation} in {metrics.duration:.3f}s (success: {success})"
        )
        
        if error:
            self.logger.error(f"Operation error: {error}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics"""
        if not self.metrics:
            return {"total_operations": 0}
        
        successful = [m for m in self.metrics if m.success]
        failed = [m for m in self.metrics if not m.success]
        completed = [m for m in self.metrics if m.duration is not None]
        
        durations = [m.duration for m in completed if m.duration is not None]
        
        summary = {
            "total_operations": len(self.metrics),
            "successful_operations": len(successful),
            "failed_operations": len(failed),
            "completion_rate": len(successful) / len(self.metrics) if self.metrics else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "operations_by_type": {}
        }
        
        # Group by operation type
        for metrics in self.metrics:
            op_type = metrics.operation
            if op_type not in summary["operations_by_type"]:
                summary["operations_by_type"][op_type] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_duration": 0
                }
            
            summary["operations_by_type"][op_type]["count"] += 1
            if metrics.success:
                summary["operations_by_type"][op_type]["successful"] += 1
            else:
                summary["operations_by_type"][op_type]["failed"] += 1
        
        # Calculate average durations by operation type
        for op_type in summary["operations_by_type"]:
            op_durations = [
                m.duration for m in completed 
                if m.operation == op_type and m.duration is not None
            ]
            if op_durations:
                summary["operations_by_type"][op_type]["avg_duration"] = sum(op_durations) / len(op_durations)
        
        return summary
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        metrics_data = {
            "summary": self.get_metrics_summary(),
            "detailed_metrics": [m.to_dict() for m in self.metrics],
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        self.logger.info(f"Exported {len(self.metrics)} metrics to {filepath}")
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        count = len(self.metrics)
        self.metrics.clear()
        self.logger.info(f"Cleared {count} metrics")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: Optional[str] = None, include_args: bool = False):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            metadata = {}
            if include_args:
                # Safely include arguments (avoid sensitive data)
                metadata["args_count"] = len(args)
                metadata["kwargs_keys"] = list(kwargs.keys())
            
            metrics = performance_monitor.start_operation(operation, metadata)
            
            try:
                result = await func(*args, **kwargs)
                performance_monitor.complete_operation(metrics, success=True)
                return result
            except Exception as e:
                performance_monitor.complete_operation(
                    metrics, 
                    success=False, 
                    error=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            metadata = {}
            if include_args:
                metadata["args_count"] = len(args)
                metadata["kwargs_keys"] = list(kwargs.keys())
            
            metrics = performance_monitor.start_operation(operation, metadata)
            
            try:
                result = func(*args, **kwargs)
                performance_monitor.complete_operation(metrics, success=True)
                return result
            except Exception as e:
                performance_monitor.complete_operation(
                    metrics, 
                    success=False, 
                    error=str(e)
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Context manager for monitoring code blocks
class monitor_operation:
    """Context manager for monitoring code blocks"""
    
    def __init__(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.metrics: Optional[PerformanceMetrics] = None
    
    def __enter__(self):
        self.metrics = performance_monitor.start_operation(self.operation, self.metadata)
        return self.metrics
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.metrics:
            success = exc_type is None
            error = str(exc_val) if exc_val else None
            performance_monitor.complete_operation(self.metrics, success=success, error=error)