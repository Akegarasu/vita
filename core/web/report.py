from flask import Flask, render_template

app = Flask(__name__,
            static_folder='./templates/',
            static_url_path='/')

def func():
    # for test
    context = {
        'username': "1",
        'age': "18",
        'gender': "2",
        'flag': "3",
        'hero': "4",
        'person': 'dell',
        'wwwurl': {
            'baidu': 'www.baidu.com',
            'google': 'www.google.com'
        }
    }
    return context

@app.route('/')
def hello():
    return render_template('advanced_table.html', **func())



if __name__ == '__main__':
    app.run(port=55000, host='0.0.0.0')