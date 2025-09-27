#  flask --app backend run

from . import app

if __name__ == '__main__':
    app.run(debug=True)