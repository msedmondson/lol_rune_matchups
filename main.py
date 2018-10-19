# add a shebang for the virtualenv #!/venv/bin/python
from app import app
app.run(debug=True, use_reloader=False)

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=9999)
