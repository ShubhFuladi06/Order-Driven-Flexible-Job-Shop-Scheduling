"""
Hybrid GA-VNS Algorithm for Flexible Job Shop Scheduling Problem (FJSP)
This module implements a hybrid approach combining Genetic Algorithm with Variable Neighborhood Search
"""

import os
import json
import random
import copy
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
from flexible_scheduling.fjsp_scheduler import Job, Order, Task, ScheduledTask, MachineState

@dataclass
class Individual:
    """Represents an individual in the GA population"""
    machine_assignment: List[int]  # Machine assignment for each operation
    operation_sequence: List[int]  # Operation sequence
    fitness: float = float('inf')  # Weighted fitness for optimization (lower is better)
    actual_makespan: float = float('inf')  # Real makespan value for reporting
    schedule: List[ScheduledTask] = field(default_factory=list)

class HybridGAVNSScheduler:
    """Hybrid Genetic Algorithm with Variable Neighborhood Search for FJSP"""
    
    def __init__(self, machine_env_file: str, user_orders_folder: str):
        self.machine_env_file = machine_env_file
        self.user_orders_folder = user_orders_folder
        self.jobs = {}
        self.orders = []
        self.machines = {}
        self.job_operation_mapping = {
            'pants': 'Job1',
            'pant': 'Job1', 
            'shirt': 'Job2',
            'curtain': 'Job3',
            'towel': 'Job4',
            't-shirt': 'Job5',
            't-shirts': 'Job5'
        }
        
        # GA Parameters - Final optimization for beating greedy
        self.population_size = 35   # Larger population for more exploration
        self.generations = 50       # More generations for better solutions
        self.crossover_rate = 0.88  # High crossover rate
        self.mutation_rate = 0.08   # Lower mutation to preserve good solutions
        self.elite_size = 7         # More elite preservation
        
        # VNS Parameters - Intensive for final optimization
        self.vns_iterations = 8     # Higher local search intensity
        self.max_neighborhoods = 4  # Full neighborhood coverage
        
        # ULTRA-ADVANCED optimization parameters
        self.critical_path_focus = True
        self.adaptive_operators = True
        self.local_search_intensity = 'ultra'
        self.convergence_threshold = 0.00001   # Ultra-strict convergence
        self.diversity_maintenance = True
        
        # Enhanced optimization features for better makespan
        self.use_memetic_algorithm = True      # Enable hybrid GA with local search
        self.use_island_model = False          # Keep disabled for speed
        self.use_opposition_learning = True    # Enable for diversity
        self.use_dynamic_parameters = True     # Enable adaptive control
        self.use_archive_solutions = True      # Enable solution archive
        
        # Archive and diversity management - Enhanced
        self.solution_archive = []
        self.archive_size = 30
        self.diversity_threshold = 0.15
        
        # Island model parameters - Disabled
        self.num_islands = 1
        self.migration_rate = 0.05
        self.migration_interval = 25
        
        # MAXIMUM makespan-focused sequence priority weights
        self.sequence_priority_weights = {
            'makespan': 0.95,        # MAXIMUM focus on makespan (95%)
            'load_balance': 0.03,    # Minimal load balancing  
            'flow_time': 0.02        # Minimal flow time consideration
        }
        
        # Enhanced optimization features for makespan minimization
        self.use_simulated_annealing = False  # Keep disabled for speed
        self.use_tabu_search = True           # Enable tabu search for better exploration
        self.use_path_relinking = False       # Keep disabled for speed
        self.use_pareto_optimization = False  # Keep disabled for speed
        self.use_smart_initialization = True  # Enable intelligent seeding
        self.use_adaptive_crossover = True    # Enable dynamic crossover
        
        # Enhanced search parameters
        self.tabu_list = []                   # Initialize tabu list
        self.tabu_tenure = 15                 # Optimal tabu tenure
        
        # Problem data
        self.all_operations = []
        self.operation_to_machines = {}
        self.machine_to_operations = defaultdict(list)
        
    def load_machine_environment(self):
        """Load machine environment and job definitions (same as original)"""
        
        # Job definitions
        job_definitions = {
            'Job1': {  # Pants
                'name': 'Pants',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job2': {  # Shirt
                'name': 'Shirt',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job3': {  # Curtain
                'name': 'Curtain',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job4': {  # Towel
                'name': 'Towel',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job5': {  # T-shirt
                'name': 'T-shirt',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            }
        }
        
        # Load processing times from file (same logic as original)
        processing_times = {}
        try:
            with open(self.machine_env_file, 'r') as f:
                lines = f.readlines()
                
            first_line = list(map(int, lines[0].strip().split()))
            num_jobs = first_line[0]
            total_machines = first_line[1]
            
            for i in range(num_jobs):
                if i + 1 < len(lines):
                    parts = list(map(int, lines[i + 1].strip().split()))
                    job_id = f'Job{i+1}'
                    
                    if job_id in job_definitions:
                        num_operations = parts[0]
                        processing_times[job_id] = {}
                        
                        idx = 1
                        for op in range(num_operations):
                            if idx >= len(parts):
                                break
                            num_machines = parts[idx]
                            idx += 1
                            operation_times = {}
                            
                            for m in range(num_machines):
                                if idx + 1 < len(parts):
                                    machine_id = f'M{parts[idx]}'
                                    processing_time = parts[idx + 1]
                                    operation_times[machine_id] = processing_time
                                    idx += 2
                                else:
                                    break
                                    
                            processing_times[job_id][op] = operation_times
                        
        except Exception as e:
            print(f"Error loading machine environment: {e}")
            # Default processing times
            for job_id in job_definitions:
                processing_times[job_id] = {}
                for op_idx in range(6):
                    processing_times[job_id][op_idx] = {}
                    if op_idx == 0:  # Fabric Inspection
                        processing_times[job_id][op_idx] = {'M1': 12, 'M2': 15, 'M3': 13, 'M4': 11}
                    elif op_idx == 1:  # Cutting  
                        processing_times[job_id][op_idx] = {'M5': 18, 'M6': 22}
                    elif op_idx == 2:  # Sewing
                        processing_times[job_id][op_idx] = {'M7': 20, 'M8': 25}
                    elif op_idx == 3:  # Dyeing
                        processing_times[job_id][op_idx] = {'M9': 35, 'M10': 30, 'M11': 40}
                    elif op_idx == 4:  # Printing
                        processing_times[job_id][op_idx] = {'M12': 20, 'M13': 18, 'M14': 15, 'M15': 22}
                    elif op_idx == 5:  # Quality Control
                        processing_times[job_id][op_idx] = {'M16': 15, 'M17': 12, 'M18': 10}
        
        # Create job objects with processing times
        for job_id, job_def in job_definitions.items():
            operations = []
            for i, op_def in enumerate(job_def['operations']):
                operation = {
                    'operation': op_def['operation'],
                    'machines': op_def['machines'],
                    'processing_times': processing_times.get(job_id, {}).get(i, {})
                }
                operations.append(operation)
                
            self.jobs[job_id] = Job(name=job_def['name'], operations=operations)
        
        # Initialize all machines
        all_machine_ids = set()
        for job in self.jobs.values():
            for op in job.operations:
                all_machine_ids.update(op['machines'])
                
        for machine_id in all_machine_ids:
            self.machines[machine_id] = MachineState(machine_id)
        
    def load_user_orders(self):
        """Load all user orders from the orders folder (same as original)"""
        
        self.orders = []
        for filename in os.listdir(self.user_orders_folder):
            if filename.endswith('.json'):
                username = filename.split('_')[0]
                timestamp = filename.replace('.json', '').replace(f'{username}_', '')
                
                filepath = os.path.join(self.user_orders_folder, filename)
                with open(filepath, 'r') as f:
                    orders_data = json.load(f)
                    
                for order_data in orders_data:
                    product = order_data.get('product', '').lower()
                    quantity = int(order_data.get('quantity', 0))
                    
                    if product in self.job_operation_mapping:
                        job_name = self.job_operation_mapping[product]
                        order_id = f"{username}_{timestamp}_{product}"
                        
                        order = Order(
                            job_name=job_name,
                            quantity=quantity,
                            user=username,
                            order_id=order_id
                        )
                        self.orders.append(order)
        
    def prepare_problem_data(self):
        """Prepare problem data for GA encoding"""
        self.all_operations = []
        operation_id = 0
        
        for order in self.orders:
            job = self.jobs[order.job_name]
            for unit in range(order.quantity):
                for op_idx in range(len(job.operations)):
                    task_id = f"{order.order_id}_unit{unit}_op{op_idx}"
                    task = Task(
                        order_id=order.order_id,
                        job_name=order.job_name,
                        operation_idx=op_idx,
                        task_id=task_id
                    )
                    
                    # Store operation with its available machines
                    operation_info = {
                        'task': task,
                        'machines': job.operations[op_idx]['machines'],
                        'processing_times': job.operations[op_idx]['processing_times'],
                        'operation_id': operation_id
                    }
                    self.all_operations.append(operation_info)
                    
                    # Map operation to available machines
                    self.operation_to_machines[operation_id] = []
                    for machine in job.operations[op_idx]['machines']:
                        if machine in job.operations[op_idx]['processing_times']:
                            machine_idx = list(self.machines.keys()).index(machine)
                            self.operation_to_machines[operation_id].append(machine_idx)
                            self.machine_to_operations[machine_idx].append(operation_id)
                    
                    operation_id += 1
        
    def create_random_individual(self) -> Individual:
        """Create a random individual for GA population with some heuristic guidance"""
        num_operations = len(self.all_operations)
        
        # Smart machine assignment (prefer faster machines with some randomness)
        machine_assignment = []
        for op_id in range(num_operations):
            available_machines = self.operation_to_machines[op_id]
            op_info = self.all_operations[op_id]
            processing_times = op_info['processing_times']
            
            # Get machine IDs and their processing times
            machine_times = []
            for machine_idx in available_machines:
                machine_id = list(self.machines.keys())[machine_idx]
                proc_time = processing_times.get(machine_id, 999)  # High penalty for unavailable
                machine_times.append((machine_idx, proc_time))
            
            # Sort by processing time and add some randomness
            machine_times.sort(key=lambda x: x[1])
            
            # Select from top 50% of machines with bias towards faster ones
            top_half = machine_times[:max(1, len(machine_times) // 2)]
            if random.random() < 0.7:  # 70% chance to pick from top half
                chosen_machine = random.choice(top_half)[0]
            else:  # 30% chance for full randomness
                chosen_machine = random.choice(available_machines)
                
            machine_assignment.append(chosen_machine)
        
        # Enhanced operation sequence creation with makespan awareness
        operation_sequence = []
        remaining_ops = set(range(num_operations))
        job_progress = defaultdict(int)  # Track progress of each job unit
        machine_availability = defaultdict(float)  # Track when machines become available
        
        while remaining_ops:
            candidates = []
            for op_id in remaining_ops:
                op_info = self.all_operations[op_id]
                task = op_info['task']
                
                # Extract unit key from task_id
                unit_key = f"{task.order_id}_{task.task_id.split('_unit')[1].split('_')[0]}"
                expected_op_idx = job_progress[unit_key]
                
                # Check if this operation can be scheduled (precedence)
                if task.operation_idx == expected_op_idx:
                    candidates.append(op_id)
            
            if candidates:
                # Enhanced selection strategy for makespan minimization
                if random.random() < 0.95:  # 95% chance for EXTREME intelligent selection
                    # Calculate priority score for each candidate with EXTREME makespan focus
                    candidate_scores = []
                    for op_id in candidates:
                        machine_idx = machine_assignment[op_id]
                        machine_id = list(self.machines.keys())[machine_idx]
                        proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 10)
                        
                        # Score based on: processing time (primary), machine availability, urgency
                        machine_avail_time = machine_availability[machine_id]
                        urgency_factor = 1.0
                        
                        # EXTREME makespan focus: processing time weighted much higher
                        score = proc_time * 0.8 + machine_avail_time * 0.15 + (1 / urgency_factor) * 0.05
                        candidate_scores.append((op_id, score))
                    
                    # Select operation with best score (shortest processing time priority)
                    chosen = min(candidate_scores, key=lambda x: x[1])[0]
                else:
                    chosen = random.choice(candidates)
                    
                # Update machine availability
                machine_idx = machine_assignment[chosen]
                machine_id = list(self.machines.keys())[machine_idx]
                proc_time = self.all_operations[chosen]['processing_times'].get(machine_id, 10)
                machine_availability[machine_id] += proc_time
            else:
                # Fallback: add any remaining operation (shouldn't happen with correct logic)
                chosen = list(remaining_ops)[0]
            
            operation_sequence.append(chosen)
            remaining_ops.remove(chosen)
            
            # Update job progress
            op_info = self.all_operations[chosen]
            task = op_info['task']
            unit_key = f"{task.order_id}_{task.task_id.split('_unit')[1].split('_')[0]}"
            job_progress[unit_key] += 1
        
        return Individual(
            machine_assignment=machine_assignment,
            operation_sequence=operation_sequence
        )
        
    def create_greedy_individual(self) -> Individual:
        """Create an individual using greedy heuristic similar to the original algorithm"""
        num_operations = len(self.all_operations)
        
        # Greedy machine assignment (always pick fastest machine)
        machine_assignment = []
        for op_id in range(num_operations):
            available_machines = self.operation_to_machines[op_id]
            op_info = self.all_operations[op_id]
            processing_times = op_info['processing_times']
            
            # Find fastest machine
            best_machine = available_machines[0]
            best_time = float('inf')
            
            for machine_idx in available_machines:
                machine_id = list(self.machines.keys())[machine_idx]
                proc_time = processing_times.get(machine_id, 999)
                if proc_time < best_time:
                    best_time = proc_time
                    best_machine = machine_idx
                    
            machine_assignment.append(best_machine)
        
        # Greedy operation sequence (shortest processing time first, respecting precedence)
        operation_sequence = []
        remaining_ops = set(range(num_operations))
        job_progress = defaultdict(int)
        
        while remaining_ops:
            candidates = []
            for op_id in remaining_ops:
                op_info = self.all_operations[op_id]
                task = op_info['task']
                
                unit_key = f"{task.order_id}_{task.task_id.split('_unit')[1].split('_')[0]}"
                expected_op_idx = job_progress[unit_key]
                
                if task.operation_idx == expected_op_idx:
                    candidates.append(op_id)
            
            if candidates:
                # Select operation with shortest processing time
                best_candidate = min(candidates, key=lambda op_id: min(
                    self.all_operations[op_id]['processing_times'].values()
                ) if self.all_operations[op_id]['processing_times'] else 999)
                chosen = best_candidate
            else:
                chosen = list(remaining_ops)[0]
            
            operation_sequence.append(chosen)
            remaining_ops.remove(chosen)
            
            # Update job progress
            op_info = self.all_operations[chosen]
            task = op_info['task']
            unit_key = f"{task.order_id}_{task.task_id.split('_unit')[1].split('_')[0]}"
            job_progress[unit_key] += 1
        
        return Individual(
            machine_assignment=machine_assignment,
            operation_sequence=operation_sequence
        )
        
    def create_ect_individual(self) -> Individual:
        """Create individual using Earliest Completion Time heuristic"""
        num_operations = len(self.all_operations)
        
        # ECT machine assignment (consider current machine loads)
        machine_assignment = []
        machine_loads = defaultdict(float)
        
        for op_id in range(num_operations):
            available_machines = self.operation_to_machines[op_id]
            op_info = self.all_operations[op_id]
            processing_times = op_info['processing_times']
            
            # Find machine with earliest completion time
            best_machine = None
            min_completion_time = float('inf')
            
            for machine_idx in available_machines:
                machine_id = list(self.machines.keys())[machine_idx]
                proc_time = processing_times.get(machine_id, 999)
                completion_time = machine_loads[machine_id] + proc_time
                
                if completion_time < min_completion_time:
                    min_completion_time = completion_time
                    best_machine = machine_idx
            
            if best_machine is not None:
                machine_assignment.append(best_machine)
                machine_id = list(self.machines.keys())[best_machine]
                proc_time = processing_times.get(machine_id, 10)
                machine_loads[machine_id] += proc_time
            else:
                machine_assignment.append(random.choice(available_machines))
        
        # Create sequence with ECT priority
        operation_sequence = []
        remaining_ops = set(range(num_operations))
        job_progress = defaultdict(int)
        
        while remaining_ops:
            candidates = []
            for op_id in remaining_ops:
                op_info = self.all_operations[op_id]
                task = op_info['task']
                
                unit_key = f"{task.order_id}_{task.task_id.split('_unit')[1].split('_')[0]}"
                expected_op_idx = job_progress[unit_key]
                
                if task.operation_idx == expected_op_idx:
                    candidates.append(op_id)
            
            if candidates:
                # Select operation with shortest processing time on assigned machine
                best_candidate = min(candidates, key=lambda op_id: 
                    self.all_operations[op_id]['processing_times'].get(
                        list(self.machines.keys())[machine_assignment[op_id]], 999
                    )
                )
                chosen = best_candidate
            else:
                chosen = list(remaining_ops)[0]
            
            operation_sequence.append(chosen)
            remaining_ops.remove(chosen)
            
            # Update job progress
            op_info = self.all_operations[chosen]
            task = op_info['task']
            unit_key = f"{task.order_id}_{task.task_id.split('_unit')[1].split('_')[0]}"
            job_progress[unit_key] += 1
        
        return Individual(
            machine_assignment=machine_assignment,
            operation_sequence=operation_sequence
        )
        
    def create_randomized_greedy_individual(self, randomness: float = 0.1) -> Individual:
        """Create individual using randomized greedy with controlled randomness"""
        num_operations = len(self.all_operations)
        
        # Randomized machine assignment (mix greedy with random)
        machine_assignment = []
        for op_id in range(num_operations):
            available_machines = self.operation_to_machines[op_id]
            op_info = self.all_operations[op_id]
            processing_times = op_info['processing_times']
            
            if random.random() < (1 - randomness):  # Greedy selection
                best_machine = None
                min_time = float('inf')
                for machine_idx in available_machines:
                    machine_id = list(self.machines.keys())[machine_idx]
                    proc_time = processing_times.get(machine_id, 999)
                    if proc_time < min_time:
                        min_time = proc_time
                        best_machine = machine_idx
                machine_assignment.append(best_machine if best_machine is not None else random.choice(available_machines))
            else:  # Random selection
                machine_assignment.append(random.choice(available_machines))
        
        # Create sequence with randomized priorities
        operation_sequence = list(range(num_operations))
        random.shuffle(operation_sequence)
        
        return Individual(
            machine_assignment=machine_assignment,
            operation_sequence=operation_sequence
        )
        
    def create_opposition_individual(self, base_individual: Individual) -> Individual:
        """Create opposition-based individual for enhanced diversity"""
        num_operations = len(self.all_operations)
        
        # Opposition machine assignment
        opposition_machines = []
        for op_id in range(num_operations):
            available_machines = self.operation_to_machines[op_id]
            base_machine = base_individual.machine_assignment[op_id]
            
            # Choose machine most different from base (opposite end of available list)
            if len(available_machines) > 1:
                available_list = list(available_machines)
                try:
                    base_idx = available_list.index(base_machine)
                    # Choose from opposite end
                    opposition_idx = len(available_list) - 1 - base_idx
                    opposition_machines.append(available_list[opposition_idx])
                except:
                    opposition_machines.append(random.choice(available_list))
            else:
                opposition_machines.append(available_machines[0])
        
        # Opposition sequence (reverse of base)
        opposition_sequence = base_individual.operation_sequence[::-1]
        
        return Individual(
            machine_assignment=opposition_machines,
            operation_sequence=opposition_sequence
        )
        
    def create_neh_individual(self) -> Individual:
        """Create individual using NEH (Nawaz-Enscore-Ham) heuristic"""
        num_operations = len(self.all_operations)
        
        # Calculate total processing time for each operation
        operation_times = []
        for op_id in range(num_operations):
            op_info = self.all_operations[op_id]
            avg_time = sum(op_info['processing_times'].values()) / len(op_info['processing_times'])
            operation_times.append((op_id, avg_time))
        
        # Sort by decreasing total processing time
        operation_times.sort(key=lambda x: x[1], reverse=True)
        
        # Assign machines based on shortest processing time
        machine_assignment = [0] * num_operations
        for op_id in range(num_operations):
            available_machines = self.operation_to_machines[op_id]
            op_info = self.all_operations[op_id]
            processing_times = op_info['processing_times']
            
            best_machine = None
            min_time = float('inf')
            for machine_idx in available_machines:
                machine_id = list(self.machines.keys())[machine_idx]
                proc_time = processing_times.get(machine_id, 999)
                if proc_time < min_time:
                    min_time = proc_time
                    best_machine = machine_idx
            
            machine_assignment[op_id] = best_machine if best_machine is not None else random.choice(available_machines)
        
        # NEH sequence construction
        operation_sequence = [operation_times[0][0]]  # Start with longest operation
        
        for i in range(1, len(operation_times)):
            op_to_insert = operation_times[i][0]
            best_pos = 0
            best_makespan = float('inf')
            
            # Try inserting at each position
            for pos in range(len(operation_sequence) + 1):
                temp_sequence = operation_sequence[:pos] + [op_to_insert] + operation_sequence[pos:]
                # Quick makespan estimation
                temp_individual = Individual(
                    machine_assignment=machine_assignment,
                    operation_sequence=temp_sequence
                )
                makespan = self.quick_makespan_estimate(temp_individual)
                
                if makespan < best_makespan:
                    best_makespan = makespan
                    best_pos = pos
            
            operation_sequence.insert(best_pos, op_to_insert)
        
        return Individual(
            machine_assignment=machine_assignment,
            operation_sequence=operation_sequence
        )
        
    def quick_makespan_estimate(self, individual: Individual) -> float:
        """Quick makespan estimation for NEH construction"""
        # Simplified makespan calculation for speed
        machine_times = defaultdict(float)
        
        for op_id in individual.operation_sequence:
            if op_id < len(individual.machine_assignment):
                machine_idx = individual.machine_assignment[op_id]
                if machine_idx < len(self.machines):
                    machine_id = list(self.machines.keys())[machine_idx]
                    if op_id < len(self.all_operations):
                        proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 10)
                        machine_times[machine_id] += proc_time
        
        return max(machine_times.values()) if machine_times else 0
        
    def evaluate_individual(self, individual: Individual) -> float:
        """Evaluate individual fitness (makespan)"""
        # Reset machine states
        machine_states = {}
        for machine_id in self.machines:
            machine_states[machine_id] = MachineState(machine_id)
        
        scheduled_tasks = []
        operation_completion_times = {}
        job_unit_completion = defaultdict(lambda: defaultdict(int))
        
        # Schedule operations according to the sequence
        for op_id in individual.operation_sequence:
            op_info = self.all_operations[op_id]
            task = op_info['task']
            
            # Get assigned machine
            machine_idx = individual.machine_assignment[op_id]
            machine_id = list(self.machines.keys())[machine_idx]
            
            # Get processing time
            processing_time = op_info['processing_times'].get(machine_id, 10)  # Default time
            
            # Calculate start time (considering precedence constraints)
            start_time = machine_states[machine_id].available_time
            
            # Check precedence constraint
            if task.operation_idx > 0:
                unit_key = task.order_id + str(task.task_id.split('_unit')[1].split('_')[0])
                prev_completion = job_unit_completion[unit_key][task.operation_idx - 1]
                start_time = max(start_time, prev_completion)
            
            # Schedule the task
            scheduled_task = machine_states[machine_id].schedule_task(task, processing_time, start_time)
            scheduled_tasks.append(scheduled_task)
            
            # Update completion tracking
            unit_key = task.order_id + str(task.task_id.split('_unit')[1].split('_')[0])
            job_unit_completion[unit_key][task.operation_idx] = scheduled_task.end_time
        
        # Calculate enhanced fitness with makespan focus and archive management
        makespan = max(task.end_time for task in scheduled_tasks) if scheduled_tasks else 0
        
        # Enhanced fitness calculation for better optimization
        individual.fitness = makespan
        individual.actual_makespan = makespan
        
        # Archive management for diversity
        if self.use_archive_solutions:
            self._update_solution_archive(individual)
            
        individual.schedule = scheduled_tasks
        return individual.fitness
        
    def _update_solution_archive(self, individual: Individual):
        """Update solution archive for diversity maintenance"""
        # Check if solution is significantly different from archived solutions
        is_diverse = True
        for archived_ind in self.solution_archive:
            similarity = self.calculate_similarity(individual, archived_ind)
            if similarity > (1 - self.diversity_threshold):
                is_diverse = False
                break
        
        if is_diverse:
            self.solution_archive.append(copy.deepcopy(individual))
            # Maintain archive size
            if len(self.solution_archive) > self.archive_size:
                # Remove worst solution from archive
                self.solution_archive.sort(key=lambda x: x.fitness)
                self.solution_archive = self.solution_archive[:self.archive_size]
                
    def _adjust_parameters_dynamically(self, generation: int, fitness_history: List[float]):
        """Dynamically adjust algorithm parameters based on progress"""
        if len(fitness_history) < 5:
            return
            
        # Check for stagnation
        recent_improvement = abs(fitness_history[-1] - fitness_history[-5]) / fitness_history[-5] if fitness_history[-5] > 0 else 0
        
        if recent_improvement < 0.01:  # Less than 1% improvement in last 5 generations
            # Increase mutation rate for more exploration
            self.mutation_rate = min(0.25, self.mutation_rate * 1.1)
            # Increase VNS intensity
            self.vns_iterations = min(12, self.vns_iterations + 1)
        else:
            # Good progress, maintain or reduce exploration
            self.mutation_rate = max(0.05, self.mutation_rate * 0.95)
            self.vns_iterations = max(3, self.vns_iterations - 1)
        
        # Adjust crossover rate based on generation progress
        generation_ratio = generation / self.generations
        if generation_ratio > 0.7:  # In final 30% of generations
            self.crossover_rate = min(0.95, self.crossover_rate * 1.05)  # Increase crossover
        
    def tournament_selection(self, population: List[Individual], tournament_size: int = 3) -> Individual:
        """Tournament selection for GA"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return min(tournament, key=lambda x: x.fitness)
        
    def order_crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Order crossover for operation sequence"""
        size = len(parent1.operation_sequence)
        
        # Crossover for operation sequence
        start, end = sorted(random.sample(range(size), 2))
        
        child1_seq = [-1] * size
        child2_seq = [-1] * size
        
        # Copy segments
        child1_seq[start:end] = parent1.operation_sequence[start:end]
        child2_seq[start:end] = parent2.operation_sequence[start:end]
        
        # Fill remaining positions
        def fill_remaining(child_seq, other_parent_seq):
            remaining = [x for x in other_parent_seq if x not in child_seq]
            j = 0
            for i in range(size):
                if child_seq[i] == -1:
                    child_seq[i] = remaining[j]
                    j += 1
        
        fill_remaining(child1_seq, parent2.operation_sequence)
        fill_remaining(child2_seq, parent1.operation_sequence)
        
        # Crossover for machine assignment
        child1_machines = []
        child2_machines = []
        for i in range(size):
            if random.random() < 0.5:
                child1_machines.append(parent1.machine_assignment[i])
                child2_machines.append(parent2.machine_assignment[i])
            else:
                child1_machines.append(parent2.machine_assignment[i])
                child2_machines.append(parent1.machine_assignment[i])
        
        child1 = Individual(machine_assignment=child1_machines, operation_sequence=child1_seq)
        child2 = Individual(machine_assignment=child2_machines, operation_sequence=child2_seq)
        
        return child1, child2
        
    def adaptive_crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Advanced adaptive crossover with multiple operators"""
        if not self.use_adaptive_crossover:
            return self.order_crossover(parent1, parent2)
        
        # Choose crossover operator based on parent similarity and generation
        similarity = self.calculate_similarity(parent1, parent2)
        generation_ratio = getattr(self, 'current_generation', 0) / self.generations
        
        if similarity > 0.7 or generation_ratio > 0.8:  # High similarity or late generation
            # Use more disruptive crossover
            return self.uniform_crossover(parent1, parent2)
        elif similarity < 0.3:  # Low similarity
            # Use preservative crossover
            return self.order_crossover(parent1, parent2)
        else:
            # Use position-based crossover
            return self.position_based_crossover(parent1, parent2)
    
    def calculate_similarity(self, ind1: Individual, ind2: Individual) -> float:
        """Calculate similarity between two individuals"""
        machine_similarity = sum(1 for i in range(len(ind1.machine_assignment)) 
                               if ind1.machine_assignment[i] == ind2.machine_assignment[i])
        machine_similarity /= len(ind1.machine_assignment)
        
        # Position-based sequence similarity
        sequence_similarity = 0
        for i in range(len(ind1.operation_sequence)):
            if i < len(ind2.operation_sequence):
                if ind1.operation_sequence[i] == ind2.operation_sequence[i]:
                    sequence_similarity += 1
        sequence_similarity /= len(ind1.operation_sequence)
        
        return (machine_similarity + sequence_similarity) / 2
    
    def uniform_crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Uniform crossover for high disruption"""
        size = len(parent1.operation_sequence)
        
        # Machine assignment uniform crossover
        child1_machines = []
        child2_machines = []
        for i in range(len(parent1.machine_assignment)):
            if random.random() < 0.5:
                child1_machines.append(parent1.machine_assignment[i])
                child2_machines.append(parent2.machine_assignment[i])
            else:
                child1_machines.append(parent2.machine_assignment[i])
                child2_machines.append(parent1.machine_assignment[i])
        
        # Sequence uniform crossover with repair
        child1_seq = []
        child2_seq = []
        used1 = set()
        used2 = set()
        
        for i in range(size):
            if random.random() < 0.5:
                if parent1.operation_sequence[i] not in used1:
                    child1_seq.append(parent1.operation_sequence[i])
                    used1.add(parent1.operation_sequence[i])
                if parent2.operation_sequence[i] not in used2:
                    child2_seq.append(parent2.operation_sequence[i])
                    used2.add(parent2.operation_sequence[i])
            else:
                if parent2.operation_sequence[i] not in used1:
                    child1_seq.append(parent2.operation_sequence[i])
                    used1.add(parent2.operation_sequence[i])
                if parent1.operation_sequence[i] not in used2:
                    child2_seq.append(parent1.operation_sequence[i])
                    used2.add(parent1.operation_sequence[i])
        
        # Fill missing operations
        all_ops = set(range(size))
        missing1 = all_ops - used1
        missing2 = all_ops - used2
        child1_seq.extend(sorted(missing1))
        child2_seq.extend(sorted(missing2))
        
        return Individual(machine_assignment=child1_machines, operation_sequence=child1_seq), \
               Individual(machine_assignment=child2_machines, operation_sequence=child2_seq)
    
    def position_based_crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Position-based crossover for moderate disruption"""
        size = len(parent1.operation_sequence)
        
        # Randomly select positions
        positions = random.sample(range(size), size // 3)
        
        # Machine assignment crossover
        child1_machines = parent1.machine_assignment[:]
        child2_machines = parent2.machine_assignment[:]
        for pos in positions:
            child1_machines[pos] = parent2.machine_assignment[pos]
            child2_machines[pos] = parent1.machine_assignment[pos]
        
        # Position-based sequence crossover
        child1_seq = [-1] * size
        child2_seq = [-1] * size
        
        # Copy selected positions
        for pos in positions:
            child1_seq[pos] = parent1.operation_sequence[pos]
            child2_seq[pos] = parent2.operation_sequence[pos]
        
        # Fill remaining positions
        def fill_remaining_pbx(child_seq, other_parent_seq, selected_ops):
            remaining = [op for op in other_parent_seq if op not in selected_ops]
            j = 0
            for i in range(size):
                if child_seq[i] == -1:
                    child_seq[i] = remaining[j]
                    j += 1
        
        selected_ops1 = {parent1.operation_sequence[pos] for pos in positions}
        selected_ops2 = {parent2.operation_sequence[pos] for pos in positions}
        
        fill_remaining_pbx(child1_seq, parent2.operation_sequence, selected_ops1)
        fill_remaining_pbx(child2_seq, parent1.operation_sequence, selected_ops2)
        
        return Individual(machine_assignment=child1_machines, operation_sequence=child1_seq), \
               Individual(machine_assignment=child2_machines, operation_sequence=child2_seq)
        
    def mutate_individual(self, individual: Individual):
        """Enhanced adaptive mutation operator for sequence optimization"""
        
        # Adaptive mutation rate based on population diversity
        adaptive_rate = self.mutation_rate
        if hasattr(self, 'current_generation') and self.current_generation > 50:
            # Increase mutation rate in later generations to escape local optima
            adaptive_rate = min(0.3, self.mutation_rate * 1.5)
        
        # Smart machine assignment mutation - focus on critical operations
        if self.critical_path_focus:
            critical_ops = self._find_critical_operations(individual)
            
            # Higher mutation probability for critical operations
            for i in range(len(individual.machine_assignment)):
                mutation_prob = adaptive_rate * 2 if i in critical_ops else adaptive_rate
                
                if random.random() < mutation_prob:
                    available_machines = self.operation_to_machines[i]
                    if len(available_machines) > 1:
                        # Prefer machines with shorter processing times
                        op_info = self.all_operations[i]
                        processing_times = op_info['processing_times']
                        
                        machine_options = []
                        for machine_idx in available_machines:
                            machine_id = list(self.machines.keys())[machine_idx]
                            proc_time = processing_times.get(machine_id, 999)
                            machine_options.append((machine_idx, proc_time))
                        
                        # Sort by processing time and select from best options
                        machine_options.sort(key=lambda x: x[1])
                        top_machines = machine_options[:max(1, len(machine_options) // 2)]
                        individual.machine_assignment[i] = random.choice(top_machines)[0]
        else:
            # Standard machine assignment mutation
            for i in range(len(individual.machine_assignment)):
                if random.random() < adaptive_rate:
                    available_machines = self.operation_to_machines[i]
                    individual.machine_assignment[i] = random.choice(available_machines)
        
        # Enhanced sequence mutation with multiple strategies
        mutation_strategy = random.choice(['swap', 'insert', 'reverse'])
        
        if random.random() < adaptive_rate:
            size = len(individual.operation_sequence)
            
            if mutation_strategy == 'swap':
                # Smart swap focusing on critical operations
                if self.critical_path_focus:
                    critical_ops = self._find_critical_operations(individual)
                    if critical_ops:
                        critical_positions = [i for i, op_id in enumerate(individual.operation_sequence) 
                                            if op_id in critical_ops]
                        if len(critical_positions) >= 2:
                            i, j = random.sample(critical_positions, 2)
                        else:
                            i = random.choice(critical_positions)
                            j = random.randint(0, size - 1)
                    else:
                        i, j = random.sample(range(size), 2)
                else:
                    i, j = random.sample(range(size), 2)
                    
                individual.operation_sequence[i], individual.operation_sequence[j] = \
                    individual.operation_sequence[j], individual.operation_sequence[i]
                    
            elif mutation_strategy == 'insert':
                # Move operation to a potentially better position
                i = random.randint(0, size - 1)
                op = individual.operation_sequence.pop(i)
                j = random.randint(0, size - 1)
                individual.operation_sequence.insert(j, op)
                
            elif mutation_strategy == 'reverse':
                # Reverse a subsequence
                start = random.randint(0, size - 1)
                end = random.randint(start, min(start + 5, size - 1))  # Limit reversal length
                individual.operation_sequence[start:end+1] = individual.operation_sequence[start:end+1][::-1]
                
    def variable_neighborhood_search(self, individual: Individual) -> Individual:
        """Enhanced Variable Neighborhood Search for better makespan optimization"""
        best_individual = copy.deepcopy(individual)
        best_fitness = individual.fitness
        
        # Use enhanced neighborhood structures for better optimization
        for neighborhood in range(1, min(self.max_neighborhoods + 1, 5)):
            current_individual = copy.deepcopy(best_individual)
            
            # Apply enhanced neighborhood structures with tabu search integration
            move_description = None
            
            if neighborhood == 1:
                # Critical path machine reassignment with tabu check
                move_description = self._critical_path_machine_reassignment_tabu(current_individual)
            elif neighborhood == 2:
                # Smart operation swapping with makespan focus
                move_description = self._makespan_focused_operation_swap(current_individual)
            elif neighborhood == 3:
                # Load balancing with critical path awareness
                move_description = self._critical_load_balancing(current_individual)
            elif neighborhood == 4:
                # Advanced sequence optimization
                move_description = self._advanced_sequence_optimization(current_individual)
            
            # Check tabu list if tabu search is enabled
            if self.use_tabu_search and move_description and move_description in self.tabu_list:
                continue  # Skip tabu moves
            
            # Evaluate the modified individual
            fitness = self.evaluate_individual(current_individual)
            
            if fitness < best_fitness:
                best_individual = current_individual
                best_fitness = fitness
                
                # Add move to tabu list if tabu search is enabled
                if self.use_tabu_search and move_description:
                    self.tabu_list.append(move_description)
                    if len(self.tabu_list) > self.tabu_tenure:
                        self.tabu_list.pop(0)
                
                break  # Move to next iteration with improved solution
                
        return best_individual
        
    def _critical_path_machine_reassignment(self, individual: Individual):
        """Enhanced Neighborhood 1: Reassign machines for critical path operations"""
        critical_ops = self._find_critical_operations(individual)
        
        for op_id in critical_ops[:5]:  # Focus on top 5 critical operations
            available_machines = self.operation_to_machines[op_id]
            if len(available_machines) > 1:
                # Find machine with minimum processing time
                best_machine = None
                min_time = float('inf')
                
                for machine_idx in available_machines:
                    machine_id = list(self.machines.keys())[machine_idx]
                    proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 10)
                    if proc_time < min_time:
                        min_time = proc_time
                        best_machine = machine_idx
                
                if best_machine is not None:
                    individual.machine_assignment[op_id] = best_machine
                
    def _smart_operation_swap(self, individual: Individual):
        """Enhanced Neighborhood 2: Smart operation swapping focusing on bottlenecks"""
        size = len(individual.operation_sequence)
        critical_ops = set(self._find_critical_operations(individual))
        
        # Prioritize swapping critical operations
        for _ in range(min(8, size // 8)):
            if critical_ops:
                # Try to swap critical operations with others
                critical_op_positions = [i for i, op_id in enumerate(individual.operation_sequence) 
                                       if op_id in critical_ops]
                if len(critical_op_positions) >= 2:
                    i, j = random.sample(critical_op_positions, 2)
                else:
                    i = random.choice(critical_op_positions)
                    j = random.randint(0, size - 1)
            else:
                i, j = random.sample(range(size), 2)
                
            individual.operation_sequence[i], individual.operation_sequence[j] = \
                individual.operation_sequence[j], individual.operation_sequence[i]
                
    def _makespan_aware_insertion(self, individual: Individual):
        """Enhanced Neighborhood 3: Insert operations with makespan awareness"""
        size = len(individual.operation_sequence)
        critical_ops = self._find_critical_operations(individual)
        
        for _ in range(min(3, size // 20)):
            # Prioritize moving critical operations to better positions
            if critical_ops:
                op_to_move = random.choice(critical_ops)
                current_pos = individual.operation_sequence.index(op_to_move)
            else:
                current_pos = random.randint(0, size - 1)
                op_to_move = individual.operation_sequence[current_pos]
            
            # Remove operation
            individual.operation_sequence.pop(current_pos)
            
            # Find best insertion position (try positions that might reduce makespan)
            best_pos = random.randint(0, len(individual.operation_sequence))
            individual.operation_sequence.insert(best_pos, op_to_move)
            
    def _job_block_swap_neighborhood(self, individual: Individual):
        """Enhanced Neighborhood 4: Swap blocks of operations from same job"""
        # Group operations by job
        job_operations = defaultdict(list)
        for i, op_id in enumerate(individual.operation_sequence):
            job_id = op_id // 100  # Assuming operation IDs encode job information
            job_operations[job_id].append(i)
        
        # Swap blocks between different jobs
        job_ids = list(job_operations.keys())
        if len(job_ids) >= 2:
            job1, job2 = random.sample(job_ids, 2)
            ops1 = job_operations[job1]
            ops2 = job_operations[job2]
            
            if ops1 and ops2:
                # Swap a random subset of operations
                swap_size1 = min(3, len(ops1))
                swap_size2 = min(3, len(ops2))
                
                swap_ops1 = random.sample(ops1, swap_size1)
                swap_ops2 = random.sample(ops2, swap_size2)
                
                for i, j in zip(swap_ops1, swap_ops2):
                    individual.operation_sequence[i], individual.operation_sequence[j] = \
                        individual.operation_sequence[j], individual.operation_sequence[i]
                        
    def _critical_operation_reschedule(self, individual: Individual):
        """New Neighborhood 5: Reschedule critical operations to earlier positions"""
        critical_ops = self._find_critical_operations(individual)
        
        for op_id in critical_ops[:3]:
            current_pos = individual.operation_sequence.index(op_id)
            # Try to move to an earlier position
            if current_pos > 0:
                new_pos = random.randint(0, current_pos - 1)
                individual.operation_sequence.pop(current_pos)
                individual.operation_sequence.insert(new_pos, op_id)
                
    def _load_balancing_neighborhood(self, individual: Individual):
        """New Neighborhood 6: Balance machine loads by reassignment"""
        # Calculate current machine loads
        machine_loads = defaultdict(float)
        for i, op_id in enumerate(individual.operation_sequence):
            machine_idx = individual.machine_assignment[op_id]
            machine_id = list(self.machines.keys())[machine_idx]
            proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 10)
            machine_loads[machine_id] += proc_time
        
        if not machine_loads:
            return
            
        # Find most and least loaded machines
        max_machine = max(machine_loads, key=machine_loads.get)
        min_machine = min(machine_loads, key=machine_loads.get)
        
        # Try to move operations from overloaded to underloaded machines
        for op_id in range(len(individual.machine_assignment)):
            current_machine_idx = individual.machine_assignment[op_id]
            current_machine_id = list(self.machines.keys())[current_machine_idx]
            
            if current_machine_id == max_machine:
                available_machines = self.operation_to_machines[op_id]
                min_machine_idx = None
                for idx, machine_id in enumerate(self.machines.keys()):
                    if machine_id == min_machine and idx in available_machines:
                        min_machine_idx = idx
                        break
                
                if min_machine_idx is not None:
                    individual.machine_assignment[op_id] = min_machine_idx
                    break  # Only reassign one operation per call
                
    def _insert_operation_neighborhood(self, individual: Individual):
        """Neighborhood 3: Insert operation at different position"""
        size = len(individual.operation_sequence)
        for _ in range(min(3, size // 20)):  # Limit number of insertions
            i = random.randint(0, size - 1)
            j = random.randint(0, size - 1)
            if i != j:
                op = individual.operation_sequence.pop(i)
                individual.operation_sequence.insert(j, op)
                
    def _block_swap_neighborhood(self, individual: Individual):
        """Neighborhood 4: Swap blocks of operations"""
        size = len(individual.operation_sequence)
        block_size = min(3, size // 10)
        
        if size > 2 * block_size:
            start1 = random.randint(0, size - block_size)
            start2 = random.randint(0, size - block_size)
            
            if abs(start1 - start2) >= block_size:  # Non-overlapping blocks
                block1 = individual.operation_sequence[start1:start1 + block_size]
                block2 = individual.operation_sequence[start2:start2 + block_size]
                
                individual.operation_sequence[start1:start1 + block_size] = block2
                individual.operation_sequence[start2:start2 + block_size] = block1
                
    def _bottleneck_elimination_neighborhood(self, individual: Individual):
        """New Neighborhood 7: Eliminate bottlenecks by intelligent reassignment"""
        # Find the most loaded machines (bottlenecks)
        machine_loads = defaultdict(float)
        operation_on_machine = defaultdict(list)
        
        for i, op_id in enumerate(individual.operation_sequence):
            machine_idx = individual.machine_assignment[op_id]
            machine_id = list(self.machines.keys())[machine_idx]
            proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 10)
            machine_loads[machine_id] += proc_time
            operation_on_machine[machine_id].append(op_id)
        
        if not machine_loads:
            return
            
        # Find most loaded machine (bottleneck)
        bottleneck_machine = max(machine_loads, key=machine_loads.get)
        bottleneck_ops = operation_on_machine[bottleneck_machine]
        
        # Try to move some operations from bottleneck to less loaded machines
        for op_id in bottleneck_ops[:3]:  # Try first 3 operations
            available_machines = self.operation_to_machines[op_id]
            best_machine = None
            min_combined_time = float('inf')
            
            for machine_idx in available_machines:
                machine_id = list(self.machines.keys())[machine_idx]
                if machine_id != bottleneck_machine:
                    proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 10)
                    combined_time = machine_loads[machine_id] + proc_time
                    if combined_time < min_combined_time:
                        min_combined_time = combined_time
                        best_machine = machine_idx
            
            if best_machine is not None:
                individual.machine_assignment[op_id] = best_machine
                break  # Move one operation at a time
                
    def _makespan_sequence_optimization(self, individual: Individual):
        """New Neighborhood 8: Direct makespan-focused sequence optimization"""
        # Find operations that finish at or near the ACTUAL makespan time
        makespan_time = individual.actual_makespan
        late_finishing_ops = []
        
        for task in individual.schedule:
            if task.end_time >= makespan_time * 0.9:  # Operations finishing in last 10%
                # Find corresponding operation ID
                for op_id, op_info in enumerate(self.all_operations):
                    if (op_info['task'].task_id == task.task_id and 
                        op_info['task'].operation_idx == task.operation_idx):
                        late_finishing_ops.append(op_id)
                        break
        
        if len(late_finishing_ops) >= 2:
            # Try to reschedule late-finishing operations earlier
            for op_id in late_finishing_ops[:2]:
                current_pos = individual.operation_sequence.index(op_id)
                # Move to an earlier position
                if current_pos > 0:
                    new_pos = max(0, current_pos - random.randint(1, min(5, current_pos)))
                    individual.operation_sequence.pop(current_pos)
                    individual.operation_sequence.insert(new_pos, op_id)
        
        # Also try swapping positions of two late operations
        if len(late_finishing_ops) >= 2:
            op1, op2 = random.sample(late_finishing_ops, 2)
            pos1 = individual.operation_sequence.index(op1)
            pos2 = individual.operation_sequence.index(op2)
            individual.operation_sequence[pos1], individual.operation_sequence[pos2] = \
                individual.operation_sequence[pos2], individual.operation_sequence[pos1]
                
    def _critical_path_machine_reassignment_tabu(self, individual: Individual) -> str:
        """Enhanced critical path machine reassignment with tabu integration"""
        critical_ops = self._find_critical_operations(individual)
        move_description = None
        
        for op_id in critical_ops[:3]:  # Focus on top 3 critical operations
            available_machines = self.operation_to_machines[op_id]
            if len(available_machines) > 1:
                current_machine = individual.machine_assignment[op_id]
                
                # Find best alternative machine
                best_machine = None
                min_time = float('inf')
                
                for machine_idx in available_machines:
                    if machine_idx != current_machine:
                        machine_id = list(self.machines.keys())[machine_idx]
                        proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 999)
                        if proc_time < min_time:
                            min_time = proc_time
                            best_machine = machine_idx
                
                if best_machine is not None:
                    old_machine = individual.machine_assignment[op_id]
                    individual.machine_assignment[op_id] = best_machine
                    move_description = f"reassign_op{op_id}_from_m{old_machine}_to_m{best_machine}"
                    break
        
        return move_description
        
    def _makespan_focused_operation_swap(self, individual: Individual) -> str:
        """Enhanced operation swapping with extreme makespan focus"""
        size = len(individual.operation_sequence)
        critical_ops = set(self._find_critical_operations(individual))
        move_description = None
        
        # Find operations that finish late
        late_operations = []
        makespan = individual.actual_makespan
        
        for i, task in enumerate(individual.schedule):
            if task.end_time >= makespan * 0.85:  # Operations finishing in last 15%
                for op_id, op_info in enumerate(self.all_operations):
                    if (op_info['task'].task_id == task.task.task_id and 
                        op_info['task'].operation_idx == task.task.operation_idx):
                        late_operations.append(op_id)
                        break
        
        # Try to swap late operations with earlier ones
        if len(late_operations) >= 2:
            op1, op2 = random.sample(late_operations, 2)
            pos1 = individual.operation_sequence.index(op1)
            pos2 = individual.operation_sequence.index(op2)
            
            # Only swap if it potentially improves position
            if abs(pos1 - pos2) > 5:  # Meaningful distance
                individual.operation_sequence[pos1], individual.operation_sequence[pos2] = \
                    individual.operation_sequence[pos2], individual.operation_sequence[pos1]
                move_description = f"swap_ops_{op1}_{op2}"
        
        return move_description
        
    def _critical_load_balancing(self, individual: Individual) -> str:
        """Load balancing with critical path awareness"""
        # Calculate machine loads and identify bottlenecks
        machine_loads = defaultdict(float)
        machine_operations = defaultdict(list)
        
        for i, op_id in enumerate(individual.operation_sequence):
            machine_idx = individual.machine_assignment[op_id]
            machine_id = list(self.machines.keys())[machine_idx]
            proc_time = self.all_operations[op_id]['processing_times'].get(machine_id, 10)
            machine_loads[machine_id] += proc_time
            machine_operations[machine_id].append(op_id)
        
        if not machine_loads:
            return None
            
        # Find most and least loaded machines
        max_machine = max(machine_loads, key=machine_loads.get)
        min_machine = min(machine_loads, key=machine_loads.get)
        
        load_difference = machine_loads[max_machine] - machine_loads[min_machine]
        
        if load_difference > machine_loads[max_machine] * 0.1:  # 10% threshold
            # Try to move operation from overloaded to underloaded machine
            overloaded_ops = machine_operations[max_machine]
            
            for op_id in overloaded_ops:
                available_machines = self.operation_to_machines[op_id]
                min_machine_idx = None
                
                for idx, machine_id in enumerate(self.machines.keys()):
                    if machine_id == min_machine and idx in available_machines:
                        min_machine_idx = idx
                        break
                
                if min_machine_idx is not None:
                    old_machine = individual.machine_assignment[op_id]
                    individual.machine_assignment[op_id] = min_machine_idx
                    return f"balance_op{op_id}_from_m{old_machine}_to_m{min_machine_idx}"
        
        return None
        
    def _advanced_sequence_optimization(self, individual: Individual) -> str:
        """Advanced sequence optimization targeting makespan reduction"""
        # Find the critical sequence of operations
        critical_ops = self._find_critical_operations(individual)
        
        if len(critical_ops) >= 2:
            # Try to reschedule critical operations earlier
            for op_id in critical_ops[:2]:
                current_pos = individual.operation_sequence.index(op_id)
                
                # Try to move critical operation to an earlier position
                if current_pos > 3:
                    # Find earliest valid position (respecting precedence)
                    new_pos = max(0, current_pos - random.randint(2, min(8, current_pos)))
                    
                    # Move operation
                    operation = individual.operation_sequence.pop(current_pos)
                    individual.operation_sequence.insert(new_pos, operation)
                    
                    return f"reschedule_critical_op{op_id}_from_{current_pos}_to_{new_pos}"
        
        return None
                
    def _smart_operation_swap_optimized(self, individual: Individual):
        """Optimized smart operation swapping focusing on bottlenecks"""
        size = len(individual.operation_sequence)
        critical_ops = set(self._find_critical_operations(individual))
        
        # Limit swaps for speed - only 2 swaps maximum
        for _ in range(min(2, size // 20)):
            if critical_ops:
                # Try to swap critical operations with others
                critical_op_positions = [i for i, op_id in enumerate(individual.operation_sequence) 
                                       if op_id in critical_ops]
                if len(critical_op_positions) >= 2:
                    i, j = random.sample(critical_op_positions, 2)
                else:
                    i = random.choice(critical_op_positions)
                    j = random.randint(0, size - 1)
            else:
                i, j = random.sample(range(size), 2)
                
            individual.operation_sequence[i], individual.operation_sequence[j] = \
                individual.operation_sequence[j], individual.operation_sequence[i]
                
    def _makespan_aware_insertion_optimized(self, individual: Individual):
        """Optimized makespan-aware insertion"""
        size = len(individual.operation_sequence)
        critical_ops = self._find_critical_operations(individual)
        
        # Only 1 insertion for speed
        if critical_ops:
            op_to_move = random.choice(critical_ops)
            current_pos = individual.operation_sequence.index(op_to_move)
        else:
            current_pos = random.randint(0, size - 1)
            op_to_move = individual.operation_sequence[current_pos]
        
        # Remove operation
        individual.operation_sequence.pop(current_pos)
        
        # Insert at a random better position
        best_pos = random.randint(0, len(individual.operation_sequence))
        individual.operation_sequence.insert(best_pos, op_to_move)
                
    def _find_critical_operations(self, individual: Individual) -> List[int]:
        """Find operations on the critical path - simplified version"""
        # Simplified critical path identification using ACTUAL makespan
        makespan = individual.actual_makespan
        critical_ops = []
        
        # Find tasks that finish at or near makespan time
        for i, task in enumerate(individual.schedule):
            if task.end_time >= makespan * 0.95:  # Within 5% of makespan
                # Find the operation ID for this task
                for op_id, op_info in enumerate(self.all_operations):
                    if (op_info['task'].task_id == task.task.task_id and 
                        op_info['task'].operation_idx == task.task.operation_idx):
                        critical_ops.append(op_id)
                        break
        
        return critical_ops[:5]  # Return at most 5 critical operations
        """Find operations on the critical path"""
        # Simplified critical path identification using ACTUAL makespan
        makespan = individual.actual_makespan
        critical_ops = []
        
        for i, task in enumerate(individual.schedule):
            if task.end_time == makespan:
                # Find the operation ID for this task
                for op_id, op_info in enumerate(self.all_operations):
                    if op_info['task'].task_id == task.task.task_id:
                        critical_ops.append(op_id)
                        break
        
        return critical_ops
        
    def genetic_algorithm(self) -> Individual:
        """Enhanced Genetic Algorithm with adaptive features for makespan minimization"""
        
        # Enhanced population initialization for better makespan
        population = []
        
        # Multi-strategy initialization for optimal starting population
        if self.use_smart_initialization:
            # Strategy 1: Greedy variants (50% of population for strong foundation)
            greedy_count = max(1, int(self.population_size * 0.5))
            for i in range(greedy_count):
                if i == 0:
                    # Pure greedy (best machine selection)
                    individual = self.create_greedy_individual()
                elif i == 1:
                    # Earliest completion time heuristic
                    individual = self.create_ect_individual()
                else:
                    # Randomized greedy with very small randomness
                    randomness = 0.02 + (i * 0.01)  # Very small randomness
                    individual = self.create_randomized_greedy_individual(randomness=randomness)
                self.evaluate_individual(individual)
                population.append(individual)
            
            # Strategy 2: Opposition-based learning (15% of population)
            if self.use_opposition_learning:
                opposition_count = max(1, int(self.population_size * 0.15))
                for i in range(opposition_count):
                    # Use different base individuals for opposition
                    base_idx = i % len(population)
                    base_individual = population[base_idx] if population else self.create_random_individual()
                    opposition_individual = self.create_opposition_individual(base_individual)
                    self.evaluate_individual(opposition_individual)
                    population.append(opposition_individual)
            else:
                opposition_count = 0
            
            # Strategy 3: Smart random individuals (15% of population)
            smart_random_count = max(1, int(self.population_size * 0.15))
            for _ in range(smart_random_count):
                individual = self.create_randomized_greedy_individual(randomness=0.1)
                self.evaluate_individual(individual)
                population.append(individual)
            
            # Strategy 4: Pure random individuals (remaining 20%)
            remaining = self.population_size - greedy_count - opposition_count - smart_random_count
        else:
            # Simple random initialization
            remaining = self.population_size
        
        # Fill remaining slots with simple random individuals
        for _ in range(remaining):
            individual = self.create_random_individual()
            self.evaluate_individual(individual)
            population.append(individual)
        
        # Sort population by fitness
        population.sort(key=lambda x: x.fitness)
        
        best_fitness_history = []
        stagnation_counter = 0
        best_ever_fitness = population[0].fitness
        
        for generation in range(self.generations):
            self.current_generation = generation  # For adaptive mutation
            
            # Dynamic parameter adjustment for better optimization
            if self.use_dynamic_parameters:
                self._adjust_parameters_dynamically(generation, best_fitness_history)
            
            new_population = []
            
            # Dynamic elitism based on population diversity
            elite_ratio = 0.2 if generation < self.generations // 2 else 0.3
            elite_count = max(1, int(self.population_size * elite_ratio))
            elite = population[:elite_count]
            new_population.extend([copy.deepcopy(ind) for ind in elite])
            
            # Apply VNS to elite individuals moderately for good optimization
            if generation % 20 == 0:  # Every 20 generations for balanced optimization
                for i in range(min(2, len(elite))):  # Apply to top 2 individuals
                    improved = self.variable_neighborhood_search(elite[i])
                    if improved.fitness < elite[i].fitness:
                        new_population[i] = improved
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)
                
                if random.random() < self.crossover_rate:
                    # Use adaptive crossover for better optimization
                    if self.use_adaptive_crossover:
                        child1, child2 = self.adaptive_crossover(parent1, parent2)
                    else:
                        child1, child2 = self.order_crossover(parent1, parent2)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                
                # Enhanced mutation
                self.mutate_individual(child1)
                self.mutate_individual(child2)
                
                # Apply VNS to promising children selectively
                if len(new_population) < self.population_size // 6:  # Apply VNS to best 15%
                    if random.random() < 0.25:  # 25% chance to apply VNS
                        child1 = self.variable_neighborhood_search(child1)
                    if random.random() < 0.25:  # 25% chance to apply VNS
                        child2 = self.variable_neighborhood_search(child2)
                
                # Evaluate after potential VNS improvement
                self.evaluate_individual(child1)
                self.evaluate_individual(child2)
                
                new_population.extend([child1, child2])
            
            # Keep only population_size individuals
            new_population = new_population[:self.population_size]
            
            # Sort by fitness
            new_population.sort(key=lambda x: x.fitness)
            population = new_population
            
            best_fitness = population[0].fitness
            best_fitness_history.append(best_fitness)
            
        return population[0]
        
    def get_schedule_data(self, best_individual: Individual) -> Dict:
        """Convert best individual to schedule data format"""
        schedule_data = {
            'tasks': [],
            'machines': list(self.machines.keys()),
            'makespan': int(best_individual.actual_makespan),
            'summary': {},
            'order_completion_times': []
        }
        
        # Calculate order completion times
        order_completion_times = {}
        for scheduled_task in best_individual.schedule:
            order_id = scheduled_task.task.order_id
            if order_id not in order_completion_times:
                order_completion_times[order_id] = 0
            order_completion_times[order_id] = max(order_completion_times[order_id], scheduled_task.end_time)
        
        # Format order completion information
        order_completion_list = []
        for order in self.orders:
            completion_time = order_completion_times.get(order.order_id, 0)
            
            # Extract product name from order_id
            product_name = order.order_id.split('_')[-1].title()
            
            order_info = {
                'user': order.user.title(),
                'product': product_name,
                'quantity': order.quantity,
                'completion_time': completion_time,
                'order_id': order.order_id,
                'job_name': order.job_name
            }
            order_completion_list.append(order_info)
        
        # Sort by completion time
        order_completion_list.sort(key=lambda x: x['completion_time'])
        schedule_data['order_completion_times'] = order_completion_list
        
        # Calculate completion time statistics
        if order_completion_list:
            completion_times = [order['completion_time'] for order in order_completion_list]
            schedule_data['completion_stats'] = {
                'fastest': min(completion_times),
                'slowest': max(completion_times),
                'average': sum(completion_times) / len(completion_times),
                'median': sorted(completion_times)[len(completion_times) // 2],
                'total_orders': len(completion_times)
            }
        else:
            schedule_data['completion_stats'] = {
                'fastest': 0,
                'slowest': 0,
                'average': 0,
                'median': 0,
                'total_orders': 0
            }
        
        # Format tasks for Gantt chart
        for scheduled_task in best_individual.schedule:
            task_data = {
                'machine': scheduled_task.machine_id,
                'job': scheduled_task.task.job_name,
                'order_id': scheduled_task.task.order_id,
                'operation': scheduled_task.task.operation_idx + 1,
                'start_time': scheduled_task.start_time,
                'end_time': scheduled_task.end_time,
                'duration': scheduled_task.processing_time,
                'task_id': scheduled_task.task.task_id
            }
            schedule_data['tasks'].append(task_data)
        
        # Summary statistics
        job_counts = defaultdict(int)
        for order in self.orders:
            job_counts[order.job_name] += order.quantity
            
        schedule_data['summary'] = {
            'total_orders': len(self.orders),
            'total_tasks': len(best_individual.schedule),
            'total_machines': len(self.machines),
            'job_distribution': dict(job_counts),
            'algorithm': 'Hybrid GA-VNS'
        }
        
        return schedule_data
        
    def run_scheduling(self) -> Dict:
        """Run the complete hybrid GA-VNS scheduling process"""
        try:
            self.load_machine_environment()
            self.load_user_orders()
            self.prepare_problem_data()
            
            if not self.all_operations:
                return {
                    'error': 'No operations to schedule',
                    'tasks': [],
                    'machines': [],
                    'makespan': 0,
                    'summary': {}
                }
            
            # Run hybrid GA-VNS algorithm
            best_solution = self.genetic_algorithm()
            
            return self.get_schedule_data(best_solution)
            
        except Exception as e:
            print(f"Error during hybrid scheduling: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'tasks': [],
                'machines': [],
                'makespan': 0,
                'summary': {}
            }

def run_hybrid_ga_vns_scheduling(machine_env_file: str, user_orders_folder: str) -> Dict:
    """Main function to run Hybrid GA-VNS scheduling"""
    scheduler = HybridGAVNSScheduler(machine_env_file, user_orders_folder)
    return scheduler.run_scheduling()

if __name__ == "__main__":
    # Test the hybrid scheduler
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    machine_env_file = os.path.join(base_dir, 'backend_data', 'factory_env', 'machineENV01.txt')
    user_orders_folder = os.path.join(base_dir, 'backend_data', 'user_orders')
    
    result = run_hybrid_ga_vns_scheduling(machine_env_file, user_orders_folder)
    print("Hybrid GA-VNS Scheduling Result:")
    print(f"Makespan: {result['makespan']} minutes")
    print(f"Total tasks: {len(result['tasks'])}")
    print(f"Algorithm: {result['summary'].get('algorithm', 'Unknown')}")