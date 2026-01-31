from tabulate import tabulate



def parse_and_display_machine_env(path):
    with open(path, 'r') as file:
        jobsNb, machinesNb = map(int, file.readline().split())
        jobs = []

        for _ in range(jobsNb):
            currentLine = list(map(int, file.readline().split()))
            operations = []
            j = 1
            while j < len(currentLine):
                k = currentLine[j]
                j += 1
                operation = []
                for _ in range(k):
                    machine = currentLine[j]
                    processingTime = currentLine[j + 1]
                    j += 2
                    operation.append({'machine': machine, 'processingTime': processingTime})
                operations.append(operation)
            jobs.append(operations)

    # Build headers
    op_titles = []
    machine_labels = []
    machine_counter = 1
    for idx, op in enumerate(jobs[0]):
        num_machines = len(op)
        op_titles.append(f"<b>Operation{idx+1}</b><br><b>{['Fabric Inspection','Cutting','Sewing','Dyeing','Printing','Quality control'][idx]}</b>")
        machine_labels.append(f"<b>Machine Group{idx+1}</b><br>({' / '.join([f'M{machine_counter+i}' for i in range(num_machines)])})")
        machine_counter += num_machines

    # Job rows
    job_names = ['Pants', 'Shirt', 'Curtain', 'Towel', 'T-shirts']
    rows_html = ""
    for i, job in enumerate(jobs):
        row_html = f"<tr><td>Job{i+1}<br>{job_names[i]}</td>"
        for op in job:
            times = " / ".join(str(m['processingTime']) for m in op)
            row_html += f"<td>{times}</td>"
        row_html += "</tr>"
        rows_html += row_html

    # Full HTML table string
    table_html = f"""
    <table class="factory-env-table">
        <thead>
            <tr>
                <th><b>Task</b></th>
                {''.join([f'<th>{title}</th>' for title in op_titles])}
            </tr>
            <tr>
                <th><b>Job/Resources</b></th>
                {''.join([f'<th>{label}</th>' for label in machine_labels])}
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    return table_html
