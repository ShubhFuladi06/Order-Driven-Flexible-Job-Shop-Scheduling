"""
Algorithm Performance Comparison Script
Compares Greedy Heuristic vs Hybrid GA-VNS for FJSP
"""

import os
import sys
import time
from typing import Dict

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_comparison():
    """Compare both algorithms and show results"""
    print("=" * 60)
    print("FJSP ALGORITHM PERFORMANCE COMPARISON")
    print("=" * 60)
    
    # File paths
    machine_env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'backend_data', 'factory_env', 'machineENV01.txt')
    user_orders_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'backend_data', 'user_orders')
    
    # Test Greedy Algorithm
    print("\n1. GREEDY HEURISTIC ALGORITHM")
    print("-" * 30)
    start_time = time.time()
    
    try:
        from flexible_scheduling.fjsp_scheduler import run_fjsp_scheduling
        greedy_result = run_fjsp_scheduling(machine_env_file, user_orders_folder)
        greedy_time = time.time() - start_time
        
        if 'error' in greedy_result:
            print(f"❌ Error: {greedy_result['error']}")
        else:
            print(f"✅ Makespan: {greedy_result['makespan']} minutes")
            print(f"⏱️  Execution Time: {greedy_time:.2f} seconds")
            print(f"📊 Tasks Scheduled: {len(greedy_result['tasks'])}")
            print(f"🏭 Machines Used: {greedy_result['summary']['total_machines']}")
            
    except Exception as e:
        print(f"❌ Error running greedy algorithm: {e}")
        greedy_result = None
        greedy_time = None
    
    # Test Hybrid GA-VNS Algorithm
    print("\n2. HYBRID GA-VNS ALGORITHM")
    print("-" * 30)
    start_time = time.time()
    
    try:
        from flexible_scheduling.hybrid_ga_vns_scheduler import run_hybrid_ga_vns_scheduling
        hybrid_result = run_hybrid_ga_vns_scheduling(machine_env_file, user_orders_folder)
        hybrid_time = time.time() - start_time
        
        if 'error' in hybrid_result:
            print(f"❌ Error: {hybrid_result['error']}")
        else:
            print(f"✅ Makespan: {hybrid_result['makespan']} minutes")
            print(f"⏱️  Execution Time: {hybrid_time:.2f} seconds")
            print(f"📊 Tasks Scheduled: {len(hybrid_result['tasks'])}")
            print(f"🏭 Machines Used: {hybrid_result['summary']['total_machines']}")
            
    except Exception as e:
        print(f"❌ Error running hybrid algorithm: {e}")
        hybrid_result = None
        hybrid_time = None
    
    # Comparison Summary
    print("\n3. COMPARISON SUMMARY")
    print("=" * 60)
    
    if greedy_result and hybrid_result and 'error' not in greedy_result and 'error' not in hybrid_result:
        greedy_makespan = greedy_result['makespan']
        hybrid_makespan = hybrid_result['makespan']
        
        improvement = ((greedy_makespan - hybrid_makespan) / greedy_makespan) * 100
        time_ratio = hybrid_time / greedy_time if greedy_time > 0 else 0
        
        print(f"📈 Makespan Improvement: {improvement:.2f}%")
        print(f"   Greedy:     {greedy_makespan} minutes")
        print(f"   Hybrid:     {hybrid_makespan} minutes")
        print(f"   Difference: {greedy_makespan - hybrid_makespan} minutes")
        print()
        print(f"⏱️  Time Comparison:")
        print(f"   Greedy:     {greedy_time:.2f} seconds")
        print(f"   Hybrid:     {hybrid_time:.2f} seconds")
        print(f"   Ratio:      {time_ratio:.1f}x slower")
        print()
        
        if improvement > 0:
            print("🏆 WINNER: Hybrid GA-VNS (Better solution quality)")
        elif improvement == 0:
            print("🤝 TIE: Both algorithms achieved same makespan")
        else:
            print("🏆 WINNER: Greedy Heuristic (Better makespan)")
            
        print()
        print("💡 RECOMMENDATIONS:")
        if improvement > 5:
            print("   • Use Hybrid GA-VNS for production scheduling")
            print("   • Significant quality improvement justifies longer computation")
        elif improvement > 0:
            print("   • Use Hybrid GA-VNS when quality is critical")
            print("   • Use Greedy for real-time scheduling needs")
        else:
            print("   • Use Greedy Heuristic for this problem instance")
            print("   • Hybrid algorithm may need parameter tuning")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    run_comparison()