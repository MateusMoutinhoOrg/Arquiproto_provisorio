# SettingsSecurity

Change of password and deletion of the account.

## Items

- home link → Home/initial
- tasks link → Tasks/initial
- projects link → Projects/initial
- settings link → SettingsProfile/initial
- log out link → LoginScreen/initial
- profile tab → SettingsProfile/initial
- notifications tab → SettingsNotifications/initial
- security tab → SettingsSecurity/initial
- new password input
- confirm password input
- change password button
  - if new password has fewer than 8 characters → SettingsSecurity/password_too_short
  - if new password and confirmation differ → SettingsSecurity/password_mismatch
  - else → SettingsSecurity/password_changed
- delete account button → SettingsSecurity/delete_account
