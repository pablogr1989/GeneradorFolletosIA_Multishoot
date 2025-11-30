import time
from datetime import datetime
from utils.logger import logger


class MetricsTracker:
    
    def __init__(self):
        self.start_time = None
        self.stage_times = {}
        self.total_tokens = 0
        self.token_costs = {
            "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
            "gpt-4o": {"input": 0.0025 / 1000, "output": 0.01 / 1000},
            "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000}
        }
    
    def start(self):
        self.start_time = time.time()
        logger.info("Metricas iniciadas")
    
    def record_stage(self, stage_name, duration):
        self.stage_times[stage_name] = duration
        logger.info(f"Etapa '{stage_name}': {duration:.2f}s")
    
    def add_tokens(self, model, prompt_tokens, completion_tokens):
        self.total_tokens += prompt_tokens + completion_tokens
        
        if model in self.token_costs:
            costs = self.token_costs[model]
            input_cost = prompt_tokens * costs["input"]
            output_cost = completion_tokens * costs["output"]
            total_cost = input_cost + output_cost
            
            logger.info(f"Tokens usados - Entrada: {prompt_tokens}, Salida: {completion_tokens}")
            logger.info(f"Coste estimado: {total_cost:.6f}€")
            
            return total_cost
        return 0
    
    def get_summary(self):
        if not self.start_time:
            return None
        
        total_time = time.time() - self.start_time
        
        summary = {
            "total_time": total_time,
            "stages": self.stage_times,
            "total_tokens": self.total_tokens,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def print_summary(self):
        summary = self.get_summary()
        if not summary:
            return
        
        print("\n" + "=" * 60)
        print("METRICAS DEL PROCESO")
        print("=" * 60)
        print(f"\nTiempo total: {summary['total_time']:.2f}s")
        print(f"\nTiempos por etapa:")
        for stage, duration in summary['stages'].items():
            print(f"  - {stage}: {duration:.2f}s")
        print(f"\nTokens totales usados: {summary['total_tokens']}")
        print("=" * 60)


metrics_tracker = MetricsTracker()