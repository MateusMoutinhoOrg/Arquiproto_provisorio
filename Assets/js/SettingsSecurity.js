onSubmit("password-form", function (f) {
    if (f.password.length < 8) return "SettingsSecurity/password_too_short";
    if (f.password !== f.confirm) return "SettingsSecurity/password_mismatch";
    return "SettingsSecurity/password_changed";
});
