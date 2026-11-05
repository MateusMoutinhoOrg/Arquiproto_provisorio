onSubmit("search", function (f) {
    var search = f.search.toLowerCase();
    if (search === "") return "Tasks/initial";
    if (search.indexOf("release") !== -1) return "Tasks/search_results";
    return "Tasks/no_results";
});
