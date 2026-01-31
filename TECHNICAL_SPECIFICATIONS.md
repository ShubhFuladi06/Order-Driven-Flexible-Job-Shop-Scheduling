# Technical Specifications for PhD Thesis: Flexible Job Shop Scheduling Platform

## 1. SYSTEM ARCHITECTURE OVERVIEW

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB PRESENTATION LAYER                   │
├─────────────────────────────────────────────────────────────┤
│  HTML5/CSS3/Bootstrap │  JavaScript/D3.js  │  Responsive UI │
├─────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│     Django Views     │    URL Routing     │   Template Engine│
├─────────────────────────────────────────────────────────────┤
│                    BUSINESS LOGIC LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  Order Management   │  User Authentication │  Data Validation │
├─────────────────────────────────────────────────────────────┤
│                    OPTIMIZATION ENGINE                      │
├─────────────────────────────────────────────────────────────┤
│  Hybrid GA-VNS     │    Greedy Heuristic  │   Performance    │
│   Algorithm        │      Algorithm       │    Analytics     │
├─────────────────────────────────────────────────────────────┤
│                    DATA ACCESS LAYER                        │
├─────────────────────────────────────────────────────────────┤
│   SQLite Database  │   JSON File Storage  │   Machine Config │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

**Backend Framework:**
- Django 5.1.7 (Python web framework)
- Python 3.11+ (Core programming language)
- NumPy 1.24+ (Numerical computations)
- SQLite 3.x (Database management)

**Frontend Technologies:**
- HTML5 (Semantic markup)
- CSS3 with Bootstrap 5.x (Responsive styling)
- JavaScript ES6+ (Client-side logic)
- D3.js/Chart.js (Data visualization)

**Development Tools:**
- Visual Studio Code (IDE)
- Git (Version control)
- Conda (Environment management)
- PowerShell (Terminal interface)

## 2. ALGORITHM IMPLEMENTATION DETAILS

### 2.1 Hybrid GA-VNS Core Components

#### Individual Representation
```python
@dataclass
class Individual:
    machine_assignment: List[int]     # Machine allocation for each operation
    operation_sequence: List[int]     # Scheduling sequence
    fitness: float                    # Makespan value
    actual_makespan: float           # Real completion time
    schedule: List[ScheduledTask]    # Detailed scheduling information
```

#### Population Initialization Strategies
```python
def initialize_population(self) -> List[Individual]:
    population = []
    
    # Strategy 1: Greedy-based (50%)
    greedy_count = int(self.population_size * 0.5)
    for i in range(greedy_count):
        if i == 0:
            individual = self.create_greedy_individual()
        elif i == 1:
            individual = self.create_ect_individual()
        else:
            randomness = 0.02 + (i * 0.01)
            individual = self.create_randomized_greedy_individual(randomness)
        population.append(individual)
    
    # Strategy 2: Opposition-based learning (15%)
    opposition_count = int(self.population_size * 0.15)
    for i in range(opposition_count):
        base_individual = population[i % len(population)]
        opposition_individual = self.create_opposition_individual(base_individual)
        population.append(opposition_individual)
    
    # Strategy 3: Smart random (35%)
    remaining = self.population_size - len(population)
    for _ in range(remaining):
        individual = self.create_random_individual()
        population.append(individual)
    
    return population
```

### 2.2 Genetic Operators

#### Adaptive Crossover Implementation
```python
def adaptive_crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
    similarity = self.calculate_similarity(parent1, parent2)
    generation_ratio = self.current_generation / self.generations
    
    if similarity > 0.7 or generation_ratio > 0.8:
        return self.uniform_crossover(parent1, parent2)
    elif similarity < 0.3:
        return self.order_crossover(parent1, parent2)
    else:
        return self.position_based_crossover(parent1, parent2)
```

#### Enhanced Mutation Strategy
```python
def mutate_individual(self, individual: Individual):
    adaptive_rate = self.mutation_rate
    if hasattr(self, 'current_generation') and self.current_generation > 25:
        adaptive_rate = min(0.15, self.mutation_rate * 1.2)
    
    # Critical path focused mutation
    critical_ops = self._find_critical_operations(individual)
    
    for i in range(len(individual.machine_assignment)):
        mutation_prob = adaptive_rate * 2 if i in critical_ops else adaptive_rate
        
        if random.random() < mutation_prob:
            available_machines = self.operation_to_machines[i]
            if len(available_machines) > 1:
                # Select machine with shorter processing time
                best_machine = self._select_best_machine(i, available_machines)
                individual.machine_assignment[i] = best_machine
```

### 2.3 Variable Neighborhood Search

#### Neighborhood Structures
```python
def variable_neighborhood_search(self, individual: Individual) -> Individual:
    best_individual = copy.deepcopy(individual)
    best_fitness = individual.fitness
    
    neighborhoods = [
        self._critical_path_machine_reassignment_tabu,
        self._makespan_focused_operation_swap,
        self._critical_load_balancing,
        self._advanced_sequence_optimization
    ]
    
    for neighborhood_func in neighborhoods:
        current_individual = copy.deepcopy(best_individual)
        move_description = neighborhood_func(current_individual)
        
        # Tabu check
        if self.use_tabu_search and move_description in self.tabu_list:
            continue
            
        fitness = self.evaluate_individual(current_individual)
        
        if fitness < best_fitness:
            best_individual = current_individual
            best_fitness = fitness
            
            # Update tabu list
            if self.use_tabu_search and move_description:
                self._update_tabu_list(move_description)
            break
    
    return best_individual
```

## 3. WEB PLATFORM IMPLEMENTATION

### 3.1 Django Application Structure

```
flexible_job_shop_platform/
├── core/                    # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── accounts/               # User management
│   ├── models.py          # User models
│   ├── views.py           # View controllers
│   └── urls.py            # App URLs
├── flexible_scheduling/    # Optimization engine
│   ├── fjsp_scheduler.py   # Greedy algorithm
│   ├── hybrid_ga_vns_scheduler.py  # Hybrid algorithm
│   └── utils.py           # Utility functions
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   └── accounts/          # App-specific templates
├── static/               # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Images and icons
├── backend_data/         # Data storage
│   ├── factory_env/      # Machine configurations
│   └── user_orders/      # Order JSON files
└── manage.py            # Django management script
```

### 3.2 Key Views Implementation

#### Main Scheduling View
```python
def admin_fjsp1(request):
    algorithm = request.GET.get('algorithm', 'greedy')
    
    try:
        machine_env_file = os.path.join(settings.BASE_DIR, 'backend_data', 'factory_env', 'machineENV01.txt')
        user_orders_folder = os.path.join(settings.BASE_DIR, 'backend_data', 'user_orders')
        
        if algorithm == 'hybrid':
            from flexible_scheduling.hybrid_ga_vns_scheduler import run_hybrid_ga_vns_scheduling
            schedule_data = run_hybrid_ga_vns_scheduling(machine_env_file, user_orders_folder)
        else:
            from flexible_scheduling.fjsp_scheduler import run_fjsp_scheduling
            schedule_data = run_fjsp_scheduling(machine_env_file, user_orders_folder)
        
        # Format data for template
        formatted_schedule_data = format_schedule_data_for_template(schedule_data)
        machine_utilization = get_machine_utilization(schedule_data)
        job_statistics = get_job_statistics(schedule_data)
        
        context = {
            'schedule_data': formatted_schedule_data,
            'machine_utilization': machine_utilization,
            'job_statistics': job_statistics,
            'algorithm_used': algorithm.title(),
            'makespan': schedule_data['makespan'],
            'total_tasks': len(schedule_data['tasks']),
            'total_machines': len(schedule_data['machines']),
            'order_completion_times': schedule_data.get('order_completion_times', []),
            'completion_stats': schedule_data.get('completion_stats', {}),
        }
        
        return render(request, 'accounts/admin_fjsp1.html', context)
        
    except Exception as e:
        return render(request, 'accounts/admin_fjsp1.html', {'error': str(e)})
```

### 3.3 Frontend Implementation

#### Gantt Chart Visualization
```javascript
function createGanttChart(scheduleData) {
    const svg = d3.select("#gantt-chart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);
    
    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Create scales
    const xScale = d3.scaleLinear()
        .domain([0, d3.max(scheduleData.tasks, d => d.end_time)])
        .range([0, width]);
    
    const yScale = d3.scaleBand()
        .domain(scheduleData.machines)
        .range([0, height])
        .padding(0.1);
    
    // Draw tasks
    g.selectAll(".task")
        .data(scheduleData.tasks)
        .enter()
        .append("rect")
        .attr("class", "task")
        .attr("x", d => xScale(d.start_time))
        .attr("y", d => yScale(d.machine))
        .attr("width", d => xScale(d.end_time) - xScale(d.start_time))
        .attr("height", yScale.bandwidth())
        .attr("fill", d => getJobColor(d.job))
        .on("mouseover", showTooltip)
        .on("mouseout", hideTooltip);
}
```

## 4. DATABASE DESIGN

### 4.1 Data Models

#### User Model
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Order Storage (JSON Format)
```json
{
    "user": "Kim",
    "timestamp": "20250415_080304",
    "orders": [
        {
            "product": "shirt",
            "quantity": 15,
            "priority": "normal",
            "due_date": "2025-04-20"
        },
        {
            "product": "towel",
            "quantity": 20,
            "priority": "high",
            "due_date": "2025-04-18"
        }
    ]
}
```

#### Machine Configuration
```
5 18
6 4 0 12 1 15 2 13 3 11
2 4 22 5 18
2 6 25 7 20
3 8 40 9 30 10 35
4 11 22 12 20 13 18 14 15
3 15 10 16 12 17 15
```

## 5. PERFORMANCE METRICS AND EVALUATION

### 5.1 Algorithm Performance Metrics

```python
class PerformanceMetrics:
    def __init__(self):
        self.makespan = 0
        self.total_completion_time = 0
        self.machine_utilization = {}
        self.execution_time = 0
        self.convergence_generation = 0
        
    def calculate_metrics(self, schedule_data, start_time):
        self.makespan = schedule_data['makespan']
        self.execution_time = time.time() - start_time
        self.machine_utilization = self._calculate_utilization(schedule_data)
        
    def _calculate_utilization(self, schedule_data):
        utilization = {}
        for machine in schedule_data['machines']:
            total_work_time = sum(
                task['duration'] for task in schedule_data['tasks'] 
                if task['machine'] == machine
            )
            utilization[machine] = (total_work_time / self.makespan) * 100
        return utilization
```

### 5.2 Statistical Analysis Framework

```python
def statistical_analysis(results_list):
    makespans = [result['makespan'] for result in results_list]
    
    statistics = {
        'mean': np.mean(makespans),
        'std_dev': np.std(makespans),
        'min': np.min(makespans),
        'max': np.max(makespans),
        'median': np.median(makespans),
        'cv': np.std(makespans) / np.mean(makespans),
        'confidence_interval_95': np.percentile(makespans, [2.5, 97.5])
    }
    
    return statistics
```

## 6. SYSTEM REQUIREMENTS AND DEPLOYMENT

### 6.1 Hardware Requirements

**Minimum Requirements:**
- CPU: Intel Core i5 or equivalent
- RAM: 8GB
- Storage: 10GB available space
- Network: Broadband internet connection

**Recommended Requirements:**
- CPU: Intel Core i7 or equivalent
- RAM: 16GB or higher
- Storage: 20GB available space (SSD preferred)
- Network: High-speed internet connection

### 6.2 Software Dependencies

```requirements.txt
Django==5.1.7
numpy==1.24.3
python==3.11+
sqlite3==3.x
bootstrap==5.3.0
d3.js==7.x
```

### 6.3 Installation Guide

```bash
# Clone repository
git clone [repository-url]
cd flexible-job-shop-platform

# Create virtual environment
conda create -n fjsp-platform python=3.11
conda activate fjsp-platform

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 7. VALIDATION AND TESTING

### 7.1 Algorithm Validation
- Unit tests for individual components
- Integration tests for complete workflow
- Performance benchmarking against literature
- Stress testing with large datasets

### 7.2 Web Platform Testing
- Functional testing of user interfaces
- Cross-browser compatibility testing
- Mobile responsiveness verification
- Security penetration testing

### 7.3 User Acceptance Testing
- Production manager feedback sessions
- Usability studies with domain experts
- Performance evaluation in real environments
- Training effectiveness assessment

---

## CONCLUSION

This technical specification provides a comprehensive foundation for PhD thesis documentation, demonstrating the depth of research, implementation excellence, and practical significance of the Flexible Job Shop Scheduling Platform. The combination of theoretical innovation and practical implementation represents a significant contribution to both academic research and industrial applications.

**Research Impact:**
- Novel hybrid metaheuristic algorithm design
- Production-ready web platform implementation
- Comprehensive experimental validation
- Open-source contribution to research community

**Industrial Value:**
- Immediate deployment capability
- Significant performance improvements
- User-friendly interface design
- Scalable architecture for enterprise use

This documentation serves as the technical backbone for a comprehensive PhD thesis that bridges the gap between theoretical research and practical industrial applications.