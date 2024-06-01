from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/sort', methods=['POST'])
def sort_entries():
    data = request.json
    entries = data.get('entries', [])
    sort_key = data.get('sort_key', 'cleanser')
    sort_order = data.get('sort_order', 'asc')

    print("Received entries for sorting:")
    # print("entries)  # Debug print

    reverse = True if sort_order == 'desc' else False
    sorted_entries = sorted(entries, key=lambda x: x[sort_key].lower() if isinstance(x[sort_key], str) else x[sort_key],
                            reverse=reverse)

    # print("Sorted entries:", sorted_entries)  # Debug print
    print("Sorted entries successfully")

    return jsonify(sorted_entries)


if __name__ == '__main__':
    app.run(port=5001)