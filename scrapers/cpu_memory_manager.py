import psutil
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CPUMemoryManagerClass:
    """Manage CPU cores and memory for optimal performance"""
    
    def __init__(self):
        self.cpu_info = self._get_cpu_info()
        logger.info(f"CPU: {self.cpu_info['physical_cores']} physical, "
                   f"{self.cpu_info['logical_cores']} logical cores")
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information"""
        return {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_usage': psutil.cpu_percent(interval=0.1, percpu=True),
            'memory': psutil.virtual_memory()
        }
    
    def get_optimal_worker_count(self) -> int:
        """Calculate optimal number of workers based on system resources"""
        cpu_info = self.cpu_info
        
        available_cores = max(1, cpu_info['logical_cores'] - 1)
        
        available_memory_gb = cpu_info['memory'].available / (1024**3)
        max_by_memory = int(available_memory_gb / 0.3)
        
        avg_cpu_load = sum(cpu_info['cpu_usage']) / len(cpu_info['cpu_usage'])
        if avg_cpu_load > 70:
            available_cores = max(1, available_cores // 2)
        
        optimal_workers = min(available_cores, max_by_memory, 8)  
        
        logger.info(f"Optimal workers: {optimal_workers} "
                   f"(Cores: {available_cores}, "
                   f"Memory allows: {max_by_memory}, "
                   f"CPU load: {avg_cpu_load:.1f}%)")
        
        return optimal_workers
    
    def set_worker_affinity(self, worker_id: int):
        """Set CPU affinity for worker process"""
        try:
            logical_cores = self.cpu_info['logical_cores']
            
            core_id = worker_id % logical_cores
            process = psutil.Process()
            process.cpu_affinity([core_id])
            
            logger.debug(f"Worker {worker_id} bound to core {core_id}")
            
        except Exception as e:
            logger.warning(f"Could not set CPU affinity: {e}")
    
    def is_system_overloaded(self) -> bool:
        """Check if system is overloaded"""
        cpu_usage = psutil.cpu_percent(interval=0.5)
        memory_usage = psutil.virtual_memory().percent
        
        if cpu_usage > 85 or memory_usage > 90:
            logger.warning(f"System overloaded: CPU {cpu_usage}%, Memory {memory_usage}%")
            return True
        
        return False