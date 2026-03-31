import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db, User, History
from models.geometry import Point, Line, Triangle, Circle, Polygon

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-mini-project-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geometry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Missing fields!', 'danger')
            return redirect(url_for('register'))
            
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch user's recent history
    user_history = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).limit(10).all()
    plot_data = session.pop('plot_data', None)
    return render_template('dashboard.html', history=user_history, plot_data=plot_data)

@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    operation = request.form.get('operation')
    result = "Unknown Operation"
    input_data = ""
    plot_data = None
    
    try:
        if operation == 'distance':
            x1, y1 = float(request.form.get('x1')), float(request.form.get('y1'))
            x2, y2 = float(request.form.get('x2')), float(request.form.get('y2'))
            p1 = Point(x1, y1)
            p2 = Point(x2, y2)
            result = f"Distance: {p1.distance_to(p2)}"
            input_data = f"P1({x1},{y1}), P2({x2},{y2})"
            plot_data = {'type': 'scatter', 'x': [x1, x2], 'y': [y1, y2], 'mode': 'lines+markers', 'name': 'Distance'}
            
        elif operation == 'midpoint':
            x1, y1 = float(request.form.get('x1')), float(request.form.get('y1'))
            x2, y2 = float(request.form.get('x2')), float(request.form.get('y2'))
            p1 = Point(x1, y1)
            p2 = Point(x2, y2)
            mid = p1.midpoint(p2)
            result = f"Midpoint: \u27e8{mid.x}, {mid.y}\u27e9"
            input_data = f"P1({x1},{y1}), P2({x2},{y2})"
            plot_data = [
                {'type': 'scatter', 'x': [x1, x2], 'y': [y1, y2], 'mode': 'lines+markers', 'name': 'Line'},
                {'type': 'scatter', 'x': [mid.x], 'y': [mid.y], 'mode': 'markers', 'name': 'Midpoint', 'marker': {'size': 12, 'color': 'red'}}
            ]
            
        elif operation == 'line':
            x1, y1 = float(request.form.get('lx1')), float(request.form.get('ly1'))
            x2, y2 = float(request.form.get('lx2')), float(request.form.get('ly2'))
            p1 = Point(x1, y1)
            p2 = Point(x2, y2)
            l = Line(p1, p2)
            result = f"Length: {l.length()}, Slope: {l.slope()}"
            input_data = f"P1({x1},{y1}), P2({x2},{y2})"
            plot_data = {'type': 'scatter', 'x': [x1, x2], 'y': [y1, y2], 'mode': 'lines+markers', 'name': 'Line'}
            
        elif operation == 'triangle':
            x1, y1 = float(request.form.get('tx1')), float(request.form.get('ty1'))
            x2, y2 = float(request.form.get('tx2')), float(request.form.get('ty2'))
            x3, y3 = float(request.form.get('tx3')), float(request.form.get('ty3'))
            t = Triangle(Point(x1,y1), Point(x2,y2), Point(x3,y3))
            result = f"Area: {t.area()}, Perimeter: {t.perimeter()}"
            input_data = f"P1({x1},{y1}), P2({x2},{y2}), P3({x3},{y3})"
            plot_data = {'type': 'scatter', 'x': [x1, x2, x3, x1], 'y': [y1, y2, y3, y1], 'mode': 'lines+markers', 'fill': 'toself', 'name': 'Triangle'}
            
        elif operation == 'circle':
            cx, cy = float(request.form.get('cx')), float(request.form.get('cy'))
            r = float(request.form.get('r'))
            c = Circle(Point(cx, cy), r)
            result = f"Area: {c.area()}, Circumference: {c.circumference()}"
            input_data = f"C({cx},{cy}), r={r}"
            import math as m
            theta = [i * (2 * m.pi / 50) for i in range(51)]
            plot_data = [
                {'type': 'scatter', 'x': [cx + r * m.cos(t) for t in theta], 'y': [cy + r * m.sin(t) for t in theta], 'mode': 'lines', 'fill': 'toself', 'name': 'Circle', 'fillcolor': 'rgba(255, 100, 100, 0.2)'},
                {'type': 'scatter', 'x': [cx], 'y': [cy], 'mode': 'markers', 'name': 'Center'}
            ]
            
        elif operation == 'polygon':
            coords = request.form.get('poly_coords')
            points = []
            xs, ys = [], []
            for pair in coords.strip().split():
                x, y = map(float, pair.split(','))
                points.append(Point(x, y))
                xs.append(x)
                ys.append(y)
            p = Polygon(points)
            result = f"Perimeter: {p.perimeter()}, Area: {p.area()}"
            input_data = f"{len(points)} Points"
            xs.append(xs[0])
            ys.append(ys[0])
            plot_data = {'type': 'scatter', 'x': xs, 'y': ys, 'mode': 'lines+markers', 'fill': 'toself', 'name': 'Polygon'}

        new_history = History(user_id=current_user.id, operation_type=operation.title(), input_data=input_data, result=result)
        db.session.add(new_history)
        db.session.commit()
        flash(result, 'success')
        
        if plot_data:
            session['plot_data'] = json.dumps([plot_data] if isinstance(plot_data, dict) else plot_data)
        
    except ValueError:
        flash("Invalid input format.", "danger")
    except Exception as e:
        flash(f"Error in calculation: {str(e)}", "danger")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
