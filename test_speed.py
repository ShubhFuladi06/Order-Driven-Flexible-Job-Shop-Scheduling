#!/usr/bin/env python
"""
Test script to verify the optimized hybrid algorithm speed
"""

import time
import os
from flexible_scheduling.hybrid_ga_vns_scheduler import HybridGAVNSScheduler

def test_algorithm_speed():
    """Test the optimized algorithm speed"""
    print("Testing optimized hybrid GA-VNS algorithm speed...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    machine_env_file = os.path.join(base_dir, 'backend_data', 'factory_env', 'machineENV01.txt')
    user_orders_folder = os.path.join(base_dir, 'backend_data', 'user_orders')
    
    # Create scheduler
    scheduler = HybridGAVNSScheduler(machine_env_file, user_orders_folder)
    
    # Measure execution time
    start_time = time.time()
    
    try:
        result = scheduler.run_scheduling()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        print(f"\n=== OPTIMIZATION RESULTS ===")
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"Final Makespan: {result['makespan']} minutes")
        print(f"Total Tasks: {len(result['tasks'])}")
        print(f"Population Size: {scheduler.population_size}")
        print(f"Generations: {scheduler.generations}")
        print(f"VNS Iterations: {scheduler.vns_iterations}")
        print(f"Speed: {'FAST' if execution_time < 30 else 'MODERATE' if execution_time < 60 else 'SLOW'}")
        
        if execution_time < 30:
            print("✅ Algorithm is now optimized for fast execution!")
        elif execution_time < 60:
            print("⚠️ Algorithm runs at moderate speed")
        else:
            print("❌ Algorithm still too slow")
            
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_algorithm_speed()