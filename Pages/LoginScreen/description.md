# LoginScreen

Authentication of an existing user.

## Items

- email input
- password input
- log in button
  - if email or password is empty → LoginScreen/required_fields
  - if email is `user@example.com` and password is `password123` → Home/initial
  - else → LoginScreen/invalid_credentials
- forgot password link → ForgotPassword/initial
- create account link → CreateAccount/initial
- demo login hint
