from flask import Flask

app = Flask(__name__)

# Basic setup for the Boardy project. No routes or additional configuration added yet.

# Example endpoint
@app.route('/hello')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True) 