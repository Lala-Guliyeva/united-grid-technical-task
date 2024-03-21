from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import io
import base64
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MonitoringData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50), index=True, unique=False)
    cpu_usage = db.Column(db.Float)
    ram_usage = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

@app.route('/')
def index():
    machine_ids = [data.machine_id for data in MonitoringData.query.with_entities(MonitoringData.machine_id).distinct()]
    return render_template('index.html', machine_ids=machine_ids)

@app.route('/machines')
def get_machines():
    machine_ids = [data.machine_id for data in MonitoringData.query.with_entities(MonitoringData.machine_id).distinct()]
    return jsonify(machine_ids)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    new_data = MonitoringData(machine_id=data['machine_id'], cpu_usage=data['cpu_usage'], ram_usage=data['ram_usage'])
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Data received"}), 200

@app.route('/graph/<machine_id>', methods=['GET'])
def show_graph(machine_id):
    data = MonitoringData.query.filter_by(machine_id=machine_id).all()
    if not data:
        return "No data available for this machine.", 404

    fig = plt.figure(figsize=(10, 6))
    timestamps = [d.timestamp for d in data]
    cpu_usages = [d.cpu_usage for d in data]
    ram_usages = [d.ram_usage for d in data]

    plt.plot(timestamps, cpu_usages, label='CPU Usage (%)')
    plt.plot(timestamps, ram_usages, label='RAM Usage (%)')
    plt.xlabel('Time')
    plt.ylabel('Usage')
    plt.title(f'Usage over Time for Machine {machine_id}')
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    return '<img src="data:image/png;base64,{}">'.format(graph_url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

