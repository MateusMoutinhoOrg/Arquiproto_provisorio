onSubmit("project", function (f) {
    if (f.name === "") return "Projects/name_required";
    return "Projects/project_created";
});
