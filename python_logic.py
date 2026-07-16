# Define these at top
SOURCE_BS = "ELKLM_DEV"
TARGET_BS = "ELKLM_UAT"  # change to "ELKLM_PRD" when needed

# Task logic
if "/Tasks/" in file or "/Integrations/" in file:

    if "agentClusterVar" in data:
        data["agentClusterVar"] = TARGET_AGENT_CLUSTER

    # script reference
    if "script" in data and isinstance(data["script"], str):
        if SOURCE_BS in data["script"]: 
            data["script"] = data["script"].replace(SOURCE_BS, TARGET_BS)

    # taskMonName (Task Monitor)
    if "taskMonName" in data and isinstance(data["taskMonName"], str):
        if SOURCE_BS in data["taskMonName"]: 
            data["taskMonName"] = data["taskMonName"].replace(SOURCE_BS, TARGET_BS)

# Trigger logic
if "/Triggers/" in file:
    tasks = data.get("tasks")
    if tasks:
        if isinstance(tasks, str):
            tasks = [tasks]
        new_tasks = []
        for task in tasks:
            if SOURCE_BS in task: 
                task = task.replace(SOURCE_BS, TARGET_BS) 
            new_tasks.append(task)
        data["tasks"] = new_tasks

# ADD THIS: Handle generic values too
def replace_in_dict(d):
    for key, value in d.items():
        if isinstance(value, str):
            if SOURCE_BS in value:
                d[key] = value.replace(SOURCE_BS, TARGET_BS)
        elif isinstance(value, dict):
            replace_in_dict(value)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, str) and SOURCE_BS in item:
                    value[i] = item.replace(SOURCE_BS, TARGET_BS)
                elif isinstance(item, dict):
                    replace_in_dict(item)

replace_in_dict(data)
