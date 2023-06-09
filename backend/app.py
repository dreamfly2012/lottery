from flask import Flask, render_template, g, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import sqlite3


import uuid
from werkzeug.security import generate_password_hash, check_password_hash

USERS = [
    {"id": 1, "name": "lily", "password": generate_password_hash("123")},
    {"id": 2, "name": "tom", "password": generate_password_hash("123")},
]


class User(UserMixin):
    """用户类"""

    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        """密码验证"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        """根据用户ID获取用户实体，为 login_user 方法提供支持"""
        if not user_id:
            return None
        for user in USERS:
            if user.get("id") == user_id:
                return User(user)
        return None


# 创建Flask应用
app = Flask(__name__)
app.secret_key = "menghuiguli"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


def create_user(user_name, password):
    """创建一个用户"""
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4(),
    }
    USERS.append(user)


def get_user(user_name):
    """根据用户名获得用户记录"""
    for user in USERS:
        if user.get("name") == user_name:
            return user
    return None


@login_manager.user_loader
def load_user(user_id):
    # 这个函数将根据用户 ID 获取用户对象
    return User.get(int(user_id))


def get_db():
    if not hasattr(g, "db"):
        g.db = sqlite3.connect("../lottery.db")
    return g.db


# 定义路由，将数据展示到网页上
@app.route("/")
@login_required
def index():
    # 从数据库中获取数据
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM ssq")
    data = c.fetchall()
    # 将数据传递给网页模板
    return render_template("index.html", data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 检查用户提交的表单数据
        username = request.form["username"]
        password = request.form["password"]

        # 在这里进行用户认证
        # 检查用户名和密码是否正确
        user_info = get_user(username)  # 从用户数据中查找用户记录
        if user_info is None:
            emsg = "用户名或密码密码有误"
            flash(emsg)
        else:
            user = User(user_info)  # 创建用户实体
            if user.verify_password(password):  # 校验密码
                login_user(user)  # 创建用户 Session
                return redirect(request.args.get("next") or url_for("index"))
            else:
                emsg = "用户名或密码密码有误"
                flash(emsg)
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        # 检查用户提交的表单数据
        qihao = request.form["qihao"]
        red1 = request.form["red1"]
        red2 = request.form["red2"]
        red3 = request.form["red3"]
        red4 = request.form["red4"]
        red5 = request.form["red5"]
        red6 = request.form["red6"]
        blue = request.form["blue"]
        date = request.form["date"]

        # 进行表单数据检查
        if (
            qihao == ""
            or red1 == ""
            or red2 == ""
            or red3 == ""
            or red4 == ""
            or red5 == ""
            or red6 == ""
            or blue == ""
            or date == ""
        ):
            emsg = "表单数据不能为空"
            flash(emsg)
        else:
            conn = get_db()
            c = conn.cursor()
            c.execute(
                "INSERT INTO ssq_my(qihao, red1, red2, red3, red4, red5, red6, blue, date) values(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (qihao, red1, red2, red3, red4, red5, red6, blue, date),
            )
            conn.commit()
            conn.close()
            return redirect(request.args.get("next") or url_for("add"))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM ssq_my limit 10")
    data = c.fetchall()
    return render_template("add.html", data=data)


@app.route("/add_dlt", methods=["GET", "POST"])
@login_required
def add_dlt():
    if request.method == "POST":
        # 检查用户提交的表单数据
        qihao = request.form["qihao"]
        red1 = request.form["red1"]
        red2 = request.form["red2"]
        red3 = request.form["red3"]
        red4 = request.form["red4"]
        red5 = request.form["red5"]
        blue1 = request.form["blue1"]
        blue2 = request.form["blue2"]
        date = request.form["date"]

        # 进行表单数据检查
        if (
            qihao == ""
            or red1 == ""
            or red2 == ""
            or red3 == ""
            or red4 == ""
            or red5 == ""
            or blue1 == ""
            or blue2 == ""
            or date == ""
        ):
            emsg = "表单数据不能为空"
            flash(emsg)
        else:
            conn = get_db()
            c = conn.cursor()
            c.execute(
                "INSERT INTO dlt_my(qihao, red1, red2, red3, red4, red5,blue1, blue2, date) values(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (qihao, red1, red2, red3, red4, red5, blue1, blue2, date),
            )
            conn.commit()
            conn.close()
            return redirect(request.args.get("next") or url_for("add_dlt"))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM ssq_my limit 10")
    data = c.fetchall()
    return render_template("add_dlt.html", data=data)


@app.route('/api/dlt', methods=["GET", "POST"])
def api_dlt():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    # 从数据库中获取数据

    conn = get_db()
    c = conn.cursor()
    # 计算总记录数
    # c.execute('SELECT COUNT(*) FROM dlt')
    # total_count = c.fetchone()[0]

    # 查询当前页记录数
    # 查询当前页的记录
    c.execute('SELECT * FROM dlt LIMIT ? OFFSET ?', (per_page, offset))
    data = c.fetchall()
    conn.close()
    return data


# 启动Flask应用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
