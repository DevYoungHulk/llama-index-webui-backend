from app import create_app
import os

# 默认为开发环境，按需求修改
config_name = os.environ.get('ENV_NAME', 'development')

app = create_app(config_name)

if __name__ == '__main__':
    if config_name == 'development':
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
