#Task logic
if "/Tasks/" in file or "/Integrations/" in file:

    if "agentClusterVar" in data:
        data["agentClusterVar"] = TARGET_AGENT_CLUSTER

    # script reference
    if "script" in data and isinstance(data["script"], str):
        if SOURCE_BS in data["script"]: # changed from startswith
            data["script"] = data["script"].replace(SOURCE_BS, TARGET_BS) # removed count=1 to replace all

    # taskMonName (Task Monitor)
    if "taskMonName" in data and isinstance(data["taskMonName"], str):
        if SOURCE_BS in data["taskMonName"]: # changed from startswith
            data["taskMonName"] = data["taskMonName"].replace(SOURCE_BS, TARGET_BS)

# Trigger logic
if "/Triggers/" in file:
    tasks = data.get("tasks")
    if tasks:
        if isinstance(tasks, str):
            tasks = [tasks]
        new_tasks = []
        for task in tasks:
            if SOURCE_BS in task: # changed from startswith
                task = task.replace(SOURCE_BS, TARGET_BS) # replace all occurrences
            new_tasks.append(task)
        data["tasks"] = new_tasks
