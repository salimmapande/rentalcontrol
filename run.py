from os import truncate
from flask import app
from renting import app    



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')

    

