#imports
from flask import Flask, request, jsonify,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import send_from_directory
import os
from web3 import Web3
import json
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from neuro import extract_fields
from read_pdf import get_text_from_pathfile
from neuro_test_2 import assess_candidate_with_ai
#define app 
app = Flask(__name__)
#program configs 
UPLOAD_FOLDER_WORKER = 'profiles_photo_worker'
UPLOAD_FOLDER_EMPLOYER = 'profiles_photo_employer'
UPLOAD_FOLDER_WORKER_RESUME='resume'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DATABASE_URI = 'sqlite:///database.db'

#app configs
app.config['SQLALCHEMY_DATABASE_URI']=DATABASE_URI
app.config['UPLOAD_FOLDER_WORKER'] = UPLOAD_FOLDER_WORKER
app.config['UPLOAD_FOLDER_EMPLOYER'] = UPLOAD_FOLDER_EMPLOYER
app.config['UPLOAD_FOLDER_WORKER_RESUME'] = UPLOAD_FOLDER_WORKER_RESUME
app.config["JWT_SECRET_KEY"] = "supersecretkeyYAAHAHAHHAHAHAHAHHAHAHAHAHAHHAHAHAHAHHA"
#app defines

CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#DB models
class Workers(db.Model):
    __tablename__ = 'workers'
    #system
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    #personal info
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    birthDate = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    education = db.Column(db.String(200))
    about_me = db.Column(db.String(2000))
    resume_text = db.Column(db.String(8092))
    
    personal_contacts = db.Column(db.String(200))
    address = db.Column(db.String(200))
    expect_pay = db.Column(db.Integer)
    only_official = db.Column(db.Boolean, default=True)
    skills = db.Column(db.String(200))
    
    #work info
    company = db.Column(db.String(100))
    now_pay = db.Column(db.Integer)
    job_title = db.Column(db.String(200))
    job_expirience=db.Column(db.String(200))
    job_history = db.Column(db.String(4048))

    #functions
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Employers(db.Model):
    __tablename__ = 'employers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(2200))
    resume_parameters  = db.Column(db.String(2200))
    
    address = db.Column(db.String(250))
    phone = db.Column(db.String(50))
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
@app.route('/api/worker/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    birthDate = data.get('birthDate')
    password = data.get('password')
    phone = data.get('phone')
    name = data.get('name')

    if not email or not name or not password or not phone or not birthDate:
        return jsonify({"error": "Все поля обязательны"}), 400

    if Workers.query.filter((Workers.email == email) | (Workers.phone == phone)).first():
        return jsonify({"error": "Пользователь с таким email или номером телефона уже существует"}), 400

    user = Workers(email=email, name=name, birthDate=birthDate,phone=phone)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Пользователь зарегистрирован", "user_id": user.id}), 201
@app.route('/api/employer/register', methods=['POST'])
def register_Employers():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    name = data.get('name')

    if not email or not name or not password or not phone:
        return jsonify({"error": "Все поля обязательны"}), 400

    if Employers.query.filter((Employers.email == email) | (Employers.phone == phone)).first():
        return jsonify({"error": "Пользователь с таким email или номером телефона уже существует"}), 400

    user = Employers(email=email, name=name,phone=phone)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Пользователь зарегистрирован", "user_id": user.id}), 201

@app.route('/api/worker/login', methods=['POST'])
def login():
    data = request.json
    print(data)
    email = data.get('email')
    password = data.get('password')

    user = Workers.query.filter_by(email=email).first()
    print(user)
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token, "user_id": user.id}), 200
    return jsonify({"error": "Неверный email или пароль"}), 401
@app.route('/api/employer/login', methods=['POST'])
def login_Employers():
    data = request.json
    print(data)
    email = data.get('email')
    password = data.get('password')

    user = Employers.query.filter_by(email=email).first()
    print(user)
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token, "user_id": user.id}), 200
    return jsonify({"error": "Неверный email или пароль"}), 401

@app.route('/api/worker/update_info', methods=['POST'])
@jwt_required()
def worker_update_info():
    data = request.json
    user_id = get_jwt_identity()
    

    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400


    user = Workers.query.filter_by(id=user_id).first()
    if user:
        user.name = data.get('name') or user.name
        user.email = data.get('email') or user.email
        user.birthDate = data.get('birthday') or user.birthDate
        user.phone = data.get('phone-number') or user.phone
        user.education = data.get('education') or user.education
        user.about_me = data.get('about') or user.about_me
        user.personal_contacts = data.get('contacts') or user.personal_contacts
        db.session.commit()
        return jsonify({"message": "User data updated successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404
@app.route('/api/worker/get_user_id_info', methods=['GET'])
@jwt_required()
def get_user_id_info():
    # data = request.json
    user_id = get_jwt_identity()
    
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    user = Workers.query.filter_by(id=user_id).first()
    if user:
        user_info = {
       'id': user.id,
        'email': user.email,
        'edit-name': user.name,
        'birthday': user.birthDate,
        'phone-number': user.phone,
        'name-company': user.company,
        'education': user.education,
        'worker-salary': user.now_pay,
        'about': user.about_me,
        'worker-post': user.job_title,
        'worker-experience': user.job_expirience,
        'contacts': user.personal_contacts
        }
    else:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user_info": user_info}), 200
@app.route('/api/employer/get_worker_info', methods=['GET'])
@jwt_required()
def get_worker_info():
    user_id = get_jwt_identity()
    print(user_id)
    job_description = json.loads(Employers.query.filter_by(id=user_id).first().resume_parameters)
    # print(job_description)
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    # Получаем всех работников из базы данных
    workers = Workers.query.all()
    
    # Если работников нет
    if not workers:
        return jsonify({"error": "No workers found"}), 404

    # Собираем информацию о каждом работнике
    workers_info = []
    for worker in workers:
        worker_info = {
            'id': worker.id,
            'email': worker.email,
            'name': worker.name,
            'age': worker.birthDate,
            'phone-number': worker.phone,
            'name-company': worker.company if worker.company else "Не указано", 
            'education': worker.education if worker.education else "Не указано", 
            'worker-salary': worker.now_pay if worker.now_pay else "Не указано",  
            'about': worker.about_me if worker.about_me else "Не указано", 
            'role': worker.job_title if worker.job_title else "Не указано", 
            'experience': worker.job_expirience if worker.job_expirience else "Не указано", 
            'contacts': worker.personal_contacts if worker.personal_contacts else "Не указано",
            
        }
        # print(get_text_from_pathfile(f"{UPLOAD_FOLDER_WORKER_RESUME}/{worker.id}.pdf"))
        job_description = (
        f"Python разработчик, требования: {job_description['skills']}, "
        "Опыт работы — 5."
        )
        similarity = assess_candidate_with_ai(get_text_from_pathfile(f"{UPLOAD_FOLDER_WORKER_RESUME}/{worker.id}.pdf"), job_description)
        worker_info['similarity'] = similarity*100
        workers_info.append(worker_info)
    print(workers_info)
    return jsonify({"workers_info": workers_info}), 200

@app.route('/api/employer/save_parameters', methods=['POST'])
@jwt_required()
def save_parameters():
    data = request.json
    user_id = get_jwt_identity()
    
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    employer = Employers.query.filter_by(id=user_id).first()
    if not employer:
        return jsonify({"error": "Employer not found"}), 404

    employer.resume_parameters = json.dumps(data) 

    db.session.commit()
    return jsonify({"message": "Parameters saved successfully"}), 200

@app.route('/api/worker/upload_profile_image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    user_id = get_jwt_identity()

    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Unsupported file type"}), 400

    folder = app.config['UPLOAD_FOLDER_WORKER'] if Workers.query.filter_by(id=user_id).first() else app.config['UPLOAD_FOLDER_EMPLOYER']
    filename = f"{user_id}.{ext}"

    os.makedirs(folder, exist_ok=True)
    for existing_file in os.listdir(folder):
        if existing_file.startswith(f"{user_id}."):
            os.remove(os.path.join(folder, existing_file))

    file.save(os.path.join(folder, filename))
    return jsonify({"message": "Image uploaded successfully"}), 200

@app.route('/api/worker/get_profile_image', methods=['GET'])
@jwt_required()
def get_profile_image():
    user_id=get_jwt_identity();
    folder = app.config['UPLOAD_FOLDER_WORKER'] if user_id in [user.id for user in Workers.query.all()] else app.config['UPLOAD_FOLDER_EMPLOYER']
    for filename in os.listdir(folder):
        if filename.startswith(f"{user_id}."):
            return send_from_directory(folder, filename)

    return jsonify({"error": "Image not found"}), 404
@app.route('/api/worker/upload_resume', methods=['POST'])
@jwt_required()
def upload_resume():
    try:
        user_id = get_jwt_identity()
        if 'file' not in request.files:
            return jsonify({"error": "Файл не найден"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Имя файла пусто"}), 400
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "Unsupported file type"}), 400

        folder = app.config['UPLOAD_FOLDER_WORKER'] if Workers.query.filter_by(id=user_id).first() else app.config['UPLOAD_FOLDER_EMPLOYER']
        filename = f"{user_id}.{ext}"

        os.makedirs(folder, exist_ok=True)
        for existing_file in os.listdir(folder):
            if existing_file.startswith(f"{user_id}."):
                os.remove(os.path.join(folder, existing_file))

        file.save(os.path.join(folder, filename))
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Куда полез!?"}), 404
@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True,host='0.0.0.0', port=8093)
