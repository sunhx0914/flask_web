# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
from flask import Flask, render_template, flash, redirect, url_for, Markup

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string') # 设置密钥 由于 flash 的消息在 session 中
# 模板中Jinja2语句、表达式、注释会保留移除后的空行
app.jinja_env.trim_blocks = True        # 删除Jinja2语句后的第一个空行   trim_blocks的block指 {% ... %} 代码块
app.jinja_env.lstrip_blocks = True      # 删除Jinja2语句所在行之前的空行 和 制表符
# 宏内的空白行不受以上两个属性控制
# app.jinja_env Environment对象

user = {
    'username': 'Grey Li',
    'bio': 'A boy who loves movies and music.',
}

movies = [
    {'name': 'My Neighbor Totoro', 'year': '1988'},
    {'name': 'Three Colours trilogy', 'year': '1993'},
    {'name': 'Forrest Gump', 'year': '1994'},
    {'name': 'Perfect Blue', 'year': '1997'},
    {'name': 'The Matrix', 'year': '1999'},
    {'name': 'Memento', 'year': '2000'},
    {'name': 'The Bucket list', 'year': '2007'},
    {'name': 'Black Swan', 'year': '2010'},
    {'name': 'Gone Girl', 'year': '2014'},
    {'name': 'CoCo', 'year': '2017'},
]


@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)
# render_template() 参数 模板的文件名 flask会在templates文件夹寻找
# 其余为 关键字参数 左边为模板的变量名，右边为传入的对象
# 字符串、列表、字典、函数、类、类实例都可以传入 模板中的用法同python
# 若想函数在模板中调用，可只传入函数对象本身（函数名），在模板中再添加()调用，并传入参数


@app.route('/')
def index():
    return render_template('index.html')


# register template context handler 注册模板上下文处理函数 返回值需要为键值对的字典
@app.context_processor
def inject_info():
    foo = 'I am foo.'
    return dict(foo=foo)  # equal to: return {'foo': foo}
# 渲染任一模板时，app.context_processor 装饰器注册的模板上下文处理函数都会执行，返回值会被添加到模板中

# 还可以直接将 app.context_processor 装饰器作为方法调用，传入函数对象和可选的自定义名称
# def inject_info():
#     foo = 'I am foo.'
#     return dict(foo=foo)  # equal to: return {'foo': foo}
#
# app.context_processor(inject_info)
# 或 lambda
# app.context_processor(lambda: dict(foo = 'I am foo.'))

# register template global function 将函数注册为模板全局函数
@app.template_global()      # 可添加 name参数指定名词 默认为函数名
def bar():
    return 'I am bar.'
# app.add_template_global()


# register template filter 注册自定义过滤器
@app.template_filter()      # 可添加 name参数指定名词 默认为函数名
def musical(s):             # s 为被过滤的变量值 其为输入，返回处理后的值
    return s + Markup(' &#9835;')   # 添加音符图标
# 示例 {{ name|musical }}
# app.add_template_filter()


# register template test 测试器     接受被测试的值 返回布尔值
# 用is 连接变量和测试器   is 左侧为测试器函数第一个参数 其余可在右侧添加括号 或空格
# 如 if age is number // if foo is sameas(bar) // if foo is sameas bar
@app.template_test()        # 可添加 name参数指定名词 默认为函数名
def baz(n):
    if n == 'baz':
        return True
    return False
# app.add_template_test()

# 可以使用 app.jinja_env 添加自定义 全局对象(全局函数、全局变量)、过滤器、测试器 p87
# app.jinja_env.globals
# app.jinja_env.filters
# app.jinja_env.tests


@app.route('/watchlist2')
def watchlist_with_static():
    return render_template('watchlist_with_static.html', user=user, movies=movies)


# message flashing 消息闪现 发送的消息会存储在session中，模板中使用全局函数 get_flashed_messages()获取
@app.route('/flash')
def just_flash():
    flash('I am flash, who is looking for me? 你好，我是闪电！')
    # flash(u'你好，我是闪电！')      # u 使python将字符串编码成Unicode，并需要在首行添加编码声明 py3 可省
    return redirect(url_for('index'))


# 错误处理函数   其需附加 app.errorhandler() 装饰器 并传入错误状态码作为参数
# 404 error handler
@app.errorhandler(404)
def page_not_found(e):      # 须接受异常类作为参数 并在返回值中注明对应的状态码
    # print(e.code, e.name)
    # print(e.description)
    return render_template('errors/404.html'), 404
# http://127.0.0.1:5000/what


# 500 error handler
@app.errorhandler(500)      # 500不会提供上面的属性
def internal_server_error(e):
    return render_template('errors/500.html'), 500
