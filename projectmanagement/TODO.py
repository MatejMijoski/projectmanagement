# TODO
# 1. Change email templates in AuthenticationApp/templates - https://github.com/pennersr/django-allauth/tree/master/allauth/templates/account/email
# for email confirmation, password change and password reset

# 2. Check and fix the messages updated and files deleted i.e. check what does the Events API return and if I need that response
# or I can just use the response from the view to update/delete message/file.

# 3.


# NOTES

# 1. The code from Google API needs to be URI decoded before it's sent to /auth/google in code. It then returns a key and logs in the user.


# LINK https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=http://127.0.0.1:8000/api/auth/google/callback/&prompt=consent&response_type=code&client_id=862591916266-27gd5m00svj1ute9vb4a77e99edbe0kv.apps.googleusercontent.com&scope=openid%20email&access_type=offline
