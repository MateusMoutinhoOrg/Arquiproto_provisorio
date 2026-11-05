onSubmit("create", function (f) {
    if (f.name === "" || f.email === "" || f.password === "" || f.confirm === "") return "CreateAccount/required_fields";
    if (!isEmail(f.email)) return "CreateAccount/invalid_email";
    if (f.email === "user@example.com") return "CreateAccount/email_already_exists";
    if (f.password.length < 8) return "CreateAccount/password_too_short";
    if (f.password !== f.confirm) return "CreateAccount/password_mismatch";
    return "OnboardingWorkspace/initial";
});
