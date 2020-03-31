# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""

# from flask import Flask, request
#
# app = Flask(__name__)
#
# # 可通过 methods 为同一URL 设置多个视图函数，分别处理不同请求
# @app.route('/hello', methods=['GET', 'POST'])
# def hello():
#     name = request.args.get('name', 'Flask')
#     # get 采用键值对形式，其第二个参数为默认值
#     # if request.args['name'] 若不存在，404；开启调试 报BadRequestKeyError
#     return '<h1>Hello %s!</h1>' % name

import os
# try:
#     from urlparse import urlparse, urljoin
# except ImportError:
#     from urllib.parse import urlparse, urljoin
from urllib.parse import urlparse, urljoin

from jinja2 import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, session, jsonify

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')   # 设置密钥
# SECRET_KEY = secret string  最好写进系统环境变量  这 secret string 是示例
# 通过 os.getenv() 第二个参数为 无时默认值

# get name value from query string and cookie
@app.route('/')
@app.route('/hello')
def hello():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % escape(name)  # escape name to avoid XSS 对输入进行转义 &lt; 表示小于号
    # return different response according to the user's authentication status
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response


# redirect
@app.route('/hi')
def hi():
    return redirect(url_for('hello'))
# redirect() 生成重定向响应 默认 302 临时重定向 第二个参数可改状态码
# 程序内重定向可用 redirect(url_for(...))

# use int URL converter
@app.route('/goback/<int:year>')        # 转换变量类型    错误时，如变量为英文，404
def go_back(year):
    return 'Welcome to %d!' % (2020 - year)


# use any URL converter
@app.route('/colors/<any(blue, white, red):color>')     # 上例中特殊的 any, 需要给出可选值
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or proud or rude. %s</p>' % color
# 还有预先构建列表，再传入
# colors = ['blue', 'white', 'red']
# @app.route('/colors/<any(%s):color>' %str(colors)[1:-1])

# 请求钩子

# return error response
@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(418)
    else:
        return 'A drop of tea.'
# abort() 手动返回状态响应
# 其不需要 return ，调用后 后边的代码不再执行

# 404
@app.route('/404')
def not_found():
    abort(404)


# return response with different formats
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''Note
to: Peter
from: Jane
heading: Reminder
body: Don't forget the party!
'''
        response = make_response(body)      # 生成响应对象
        response.mimetype = 'text/plain'    # mimetype属性 设置MIME类型
    elif content_type == 'html':
        body = '''<!DOCTYPE html>
<html>
<head></head>
<body>
  <h1>Note</h1>
  <p>to: Peter</p>
  <p>from: Jane</p>
  <p>heading: Reminder</p>
  <p>body: <strong>Don't forget the party!</strong></p>
</body>
</html>
'''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'xml':
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<note>
  <to>Peter</to>
  <from>Jane</from>
  <heading>Reminder</heading>
  <body>Don't forget the party!</body>
</note>
'''
        response = make_response(body)
        response.mimetype = 'application/xml'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        response = jsonify(body)    # 默认200   可传入 普通参数/关键字参数/字典、列表、元组
        # equal to:
        # response = make_response(json.dumps(body))
        # response.mimetype = "application/json"
    else:
        abort(400)
    return response


# set cookie
@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hello')))
    response.set_cookie('name', name)
    return response


# log in user
@app.route('/login')
def login():
    session['logged_in'] = True     # 写入 session  安全的cookie
    return redirect(url_for('hello'))


# protect view
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return 'Welcome to admin page.'


# log out user
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')    # 删除 session 的 logged_in
    return redirect(url_for('hello'))


# AJAX
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)   # 生成两段随机文本
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {       // $('#load') 选择器  传入 id/class等属性 创建为jQuery对象
        $.ajax({                        // $.ajax() 等同于 jQuery.ajax()
            url: '/more',               // 目标URL
            type: 'get',                // 请求方法
            success: function(data){        // 返回2XX 响应后触发的回调函数
                $('.body').append(data);    // 将返回的响应插入到页面中
            }
        })
    })
})
</script>''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


# redirect to last page
@app.route('/foo')
def foo():
    return '<h1>Foo page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)    # full_path 如 '/hello?name=Grey'
# next 为查询参数，为当前页面URL


@app.route('/bar')
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/do-something')
def do_something():
    # print('do something here...')
    # do something here
    return redirect_back()


# 验证 next变量值/referrer 是否属于程序内部URL  不然存在 开放重定向 漏洞
def is_safe_url(target):
    ref_url = urlparse(request.host_url)    # host_url 如 'http://helloflask.com/'
    test_url = urlparse(urljoin(request.host_url, target))      # urljoin主要是拼接URL
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
    # scheme 协议  http https
    # netloc 域名  如 helloflask.com


def redirect_back(default='hello', **kwargs):
    print('request.referrer', request.referrer)
    print('request.args --', request.args)

    for target in request.args.get('next'), request.referrer:      # 查询参数 和 HTTP referer
        # 先获取next, 为空 则获取referer, 仍为空 则 默认的hello
        print('target --', target)
        if not target:      # 在Python中，None、空[]、空{}、空()、0等一系列代表空和无的对象会被转换成False。
            # 除此之外的其它对象都会被转化成True。
            # not None --> True
            # not '/bar?' --> False
            continue
        if is_safe_url(target):
            return redirect(target)     # redirect直接是url，就是app.route的路径参数
    return redirect(url_for(default, **kwargs))     # 这是执行默认 hello
