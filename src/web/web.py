# from flask import Flask, request, render_template
#
# app = Flask(__name__)
#
# # Bot configuration data (in-memory for simplicity, use a database in practice)
# bot_config = {
#     "prefix": "!",
#     "welcome_message": "Welcome to the server!",
# }
#
# @app.route('/')
# def index():
#     return render_template('index.html', config=bot_config)
#
# @app.route('/configure', methods=['POST'])
# def configure():
#     prefix = request.form.get('prefix')
#     welcome_message = request.form.get('welcome_message')
#
#     bot_config['prefix'] = prefix
#     bot_config['welcome_message'] = welcome_message
#
#     return render_template('index.html', config=bot_config, message="Configuration updated!")
#
# if __name__ == '__main__':
#     app.run(debug=True)
