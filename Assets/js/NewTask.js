onSubmit("task", function (f) {
    if (f.title === "") return "NewTask/title_required";
    return "Tasks/task_created";
});
