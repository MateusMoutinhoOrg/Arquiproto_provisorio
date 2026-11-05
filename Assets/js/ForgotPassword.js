onSubmit("forgot", function (f) {
    if (!isEmail(f.email)) return "ForgotPassword/invalid_email";
    return "ForgotPassword/email_sent";
});
