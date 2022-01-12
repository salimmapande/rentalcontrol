import os
from twilio.rest import Client



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

account_sid = "AC23ae688c6704ed6fb3b1ca2204fb9b2f"
auth_token = "5c7c47f2c39713dcf4bd2117c85ea5fa"


client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body='Payment has been made by... on ',
         from_='+(254) 279-5811',
         to='+255694064300'
     )

print(message.sid)