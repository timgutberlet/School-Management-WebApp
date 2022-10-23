from routes import *

# Starting the python applicaiton
if __name__ == '__main__':
    print("-"*70)
    print("""If you are on UCPU0: Please open your browser to: http://ucpu0.ug.cs.usyd.edu.au:"""+portchoice+"""/""")
    print("-"*70)
    print("-"*70)
    print("""If you are on Linux/Your Own Computer: Please open your browser to: http://127.0.0.1:"""+portchoice+"""/""")
    print("-"*70)
    page = {'title' : 'UniDB'}
    # Note, you're going to have to change the PORT number
    app.run(debug=True, host='0.0.0.0', port=int(portchoice))
