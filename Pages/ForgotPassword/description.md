# ForgotPassword

Request of a password reset link.

## Items

- email input
- send link button
  - if email format is invalid → ForgotPassword/invalid_email
  - else → ForgotPassword/email_sent
- back to login link → LoginScreen/initial
