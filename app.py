

from flask import Flask, render_template
from try import main

app = Flask(__name__)

def index():
    # Execute the Python code and get the results
    total_acres, total_trees = main()
    # Pass the results to the HTML template
    return render_template('index.html', total_acres=total_acres, total_trees=total_trees)

if __name__ == '__main__':
    app.run(debug=True)
