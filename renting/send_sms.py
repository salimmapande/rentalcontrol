import os
from twilio.rest import Client



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
<<<<<<< HEAD
account_sid =''# "AC23ae688c6704ed6fb3b1ca2204fb9b2f"
auth_token ='' #"5c7c47f2c39713dcf4bd2117c85ea5fa"
=======
account_sid = "AC23ae688c6704ed6fb3b1ca2204fb9b2f"
auth_token = "5c7c47f2c39713dcf4bd2117c85ea5fa"
>>>>>>> 2e129f3f78f16e9251fe983f90acdc3a1560a413
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body='Payment has been made by... on ',
         from_='+12542795811',
         to='+255694064300'
     )

print(message.sid)