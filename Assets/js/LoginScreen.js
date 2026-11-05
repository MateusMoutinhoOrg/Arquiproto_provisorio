onSubmit("login", function (f) {
    if (f.email === "" || f.password === "") return "LoginScreen/required_fields";
    if (f.email === "user@example.com" && f.password === "password123") return "Home/initial";
    return "LoginScreen/invalid_credentials";
});
