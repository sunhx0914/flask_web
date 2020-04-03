# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
from threading import Thread

import sendgrid
from sendgrid.helpers.mail import Email as SGEmail, Content, Mail as SGMail
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask import Flask, flash, redirect, url_for, render_template, request

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config.update(  # 加载配置
    SECRET_KEY=os.getenv('SECRET_KEY', 'secret string'),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),   # 发送邮件的SMTP 服务器
    MAIL_PORT=465,  # 发信端口 对应下面的加密方式  不加密时默认25
    MAIL_USE_SSL=True,  # 是否使用SSL/TLS
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),   # 发信服务器的用户名
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),   # 发信服务器的密码
    MAIL_DEFAULT_SENDER=('sunhx', os.getenv('MAIL_USERNAME'))     # 默认发信人
)

mail = Mail(app)
# 实例化Flask-Mail提供的Mail类并传入程序实例以完成初始化

"""flask shell 示例
# 邮件通过从Flask-Mail中导入的Message类表示，
# 而发信功能通过我们在程序包的构造文件中创建的mail对象实现
>>> from flask_mail import Message
>>> from app import mail
>>> message = Message(subject='Hello, World!', recipients=['xxxxxxxxxx@qq.com>'], 
    body='''Across the Great Wall we can reach every corner in the world. \n
    未来的我，腹有诗书，眼有山川日月，心有你。\n
    I LOVE YOU!\n
    -- 来自hx的电子邮件测试 (-.-)
    ''')
    # Zorn <zorn@example.com> 或者 zorn@example.com
>>> mail.send(message)
"""


# Flask-Mail通过连接SMTP（Simple Mail Transfer Protocol，简单邮件传输协议）服务器来发送邮件
# send over SMTP 通过SMTP发送
def send_smtp_mail(subject, to, body):  # 上面的flask shell 包装为了通用函数
    message = Message(subject, recipients=[to], body=body)
    # 一封邮件至少要包含主题、收件人、正文、发信人这几个元素。
    # 发信人用默认配置变量指定过了 recipients为一个包含电子邮件地址的列表。
    mail.send(message)
    # 通过对mail对象调用send()方法，传入邮件对象即可发送邮件


# send over SendGrid Web API 通过事务邮件服务发送
def send_api_mail(subject, to, body):
    # MAIL_SERVER = 'smtp.sendgrid.net'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'apikey'
    # MAIL_PASSWORD = os.getenv('SENDGRID_API_KEY')  # 从环境变量读取API密钥
    sg = sendgrid.SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    # 实例化SendGridAPIClient类创建一个发信客户端对象
    # 实例化时需要传入创建的API密钥

    # 从sendgrid.helpers.mail模块导入了三个辅助类：Email、Content和Mail
    from_email = SGEmail('Grey Li <noreply@helloflask.com>')
    # Email类用来创建邮件地址，即发信地址和收信地址 构造方法依次接收email和name参数
    # 传入值可以为三种形式：分别传入Email地址、姓名；
    # 仅传入邮箱地址；
    # 传入标准收件人字符串，即“姓名<Email地址>”。
    to_email = SGEmail(to)
    content = Content("text/plain", body)
    # Content类的构造函数接收MIME类型（type_）和正文（value）作为参数。
    email = SGMail(from_email, subject, to_email, content)
    # Mail类则用来创建邮件对象，其构造方法接收的参数分别为
    # 发信人(from_email)、主题(subject)、收信人(to_email)和邮件正文(content)
    sg.client.mail.send.post(request_body=email.get())
    # 对mail对象调用get()方法或是直接打印会看到最终生成的表示一封邮件的预JSON值
    # 通过对表示邮件客户端的sg对象调用sg.client.mail.send.post()方法，
    # 并将表示数据的字典使用关键字request_body传入即可发送发信的POST请求
    # 发信的方法会返回响应，response = sg...
    # response.status_code  response.body ...   p187


# send email asynchronously
def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


'''
因为Flask-Mail的send()方法内部的调用逻辑中使用了current_app
变量，而这个变量只在激活的程序上下文中才存在，这里在后台线程调
用发信函数，但是后台线程并没有程序上下文存在。为了正常实现发信
功能，我们传入程序实例app作为参数，并调用app.app_context()手动
激活程序上下文。
'''


# 异步发送邮件
# 原因：当使用SMTP的方式发送电子邮件时，如果你手动使用浏览器测试程序的注册功能，
# 你可能会注意到，在提交注册表单后，浏览器会有几秒钟的不响应。
# 因为这时候程序正在发送电子邮件，发信的操作阻断了请求——响应循环，
# 直到发信的send_mail()函数调用结束后，视图函数才会返回响应。
# 这几秒的延迟带来了不好的用户体验，
# 为了避免这个延迟，我们可以将发信函数放入后台线程异步执行
def send_async_mail(subject, to, body):
    # app = current_app._get_current_object()  # if use factory (i.e. create_app()), get app like this
    message = Message(subject, recipients=[to], body=body)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


# send email with HTML body
def send_subscribe_mail(subject, to, **kwargs):
    # 为了支持在调用函数时传入模板中需要的关键字参数，我们在send_mail()中接收
    # 可变长关键字参数(**kwargs)并传入render_template()函数。
    message = Message(subject, recipients=[to], sender='Flask Weekly <%s>' % os.getenv('MAIL_USERNAME'))
    message.body = render_template('emails/subscribe.txt', **kwargs)    # 纯文本邮件模板
    # 通过类属性指定正文类型  纯文本（text/plain）/HTML（text/html）
    message.html = render_template('emails/subscribe.html', **kwargs)   # HTML邮件模板
    # 在发送邮件的函数中使用render_template()函数渲染邮件正文，并传入相应的变量
    mail.send(message)


class EmailForm(FlaskForm):
    to = StringField('To', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    submit_smtp = SubmitField('Send with SMTP')
    submit_api = SubmitField('Send with SendGrid API')
    submit_async = SubmitField('Send with SMTP asynchronously')


class SubscribeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        to = form.to.data
        subject = form.subject.data
        body = form.body.data
        if form.submit_smtp.data:
            send_smtp_mail(subject, to, body)
            method = request.form.get('submit_smtp')
        elif form.submit_api.data:
            send_api_mail(subject, to, body)
            method = request.form.get('submit_api')
        else:
            send_async_mail(subject, to, body)
            method = request.form.get('submit_async')

        flash('Email sent %s! Check your inbox.' % ' '.join(method.split()[1:]))
        return redirect(url_for('index'))
    form.subject.data = 'Hello, World!'
    form.body.data = 'Across the Great Wall we can reach every corner in the world.'
    return render_template('index.html', form=form)


# 周刊订阅程序，当用户在表单中填写了正确
# 的Email地址时，我们就发送一封邮件来通知用户订阅成功
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        send_subscribe_mail('Subscribe Success!', email, name=name)
        flash('Confirmation email have been sent! Check your inbox.')
        return redirect(url_for('subscribe'))
    return render_template('subscribe.html', form=form)


@app.route('/unsubscribe')
def unsubscribe():
    flash('Want to unsubscribe? No way...')
    return redirect(url_for('subscribe'))
