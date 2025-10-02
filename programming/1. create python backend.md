

#### To create a simple Python  Flask Backend (API Service)

1. Set Up the ENV

```bash
    pip install Flask
```

2. Sample Code for a Simple Flask Web App

```python
    from flask import Flask, request, render_template, jsonify

    app = Flask(__name__)

    # Sample data to search from
    data = [
        {"id": 1, "name": "University of Arizona"},
        {"id": 2, "name": "Arizona State University"},
        {"id": 3, "name": "Harvard University"},
        {"id": 4, "name": "Stanford University"},
        {"id": 5, "name": "Massachusetts Institute of Technology"},
    ]
    # Function to perform a simple search
    def search_data(term):
        results = [item for item in data if term.lower() in item["name"].lower()]
        return results

    @app.route('/search', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            term = request.form.get('term')  # Get the search term from the form
            results = search_data(term)      # Search the data for matching entries
            return render_template('index.html', term=term, results=results)
        return render_template('index.html', term=None, results=[])

    # Run the Flask app
    if __name__ == '__main__':
        app.run(debug=True)

```

3. Endpoint

 http://localhost:5000/search?term=ariz

