# CreateAccount

Registration of a new user.

## Items

- name input
- email input
- password input
- confirm password input
- create account button
  - if any field is empty → CreateAccount/required_fields
  - if email format is invalid → CreateAccount/invalid_email
  - if email is `user@example.com` → CreateAccount/email_already_exists
  - if password has fewer than 8 characters → CreateAccount/password_too_short
  - if password and confirmation differ → CreateAccount/password_mismatch
  - else → OnboardingWorkspace/initial
- back to login link → LoginScreen/initial
