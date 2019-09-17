# test.py
 
from db_setup import init_dbfrom scorer_app import app

 
init_db()
 
 
@app.route('/test')
def test():
    return "Welcome to Flask!"
 
if __name__ == '__main__':
    app.run()