onSubmit("workspace-form", function (f) {
    if (f.workspace === "") return "OnboardingWorkspace/name_required";
    return "OnboardingInvite/initial";
});
