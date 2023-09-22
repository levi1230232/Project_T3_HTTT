from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Tinh_Hoc_Phi.db'
# app.config.from_pyfile('./config.py')

db = SQLAlchemy()
db.init_app(app)


class MonHoc(db.Model):
    __tablename__ = 'mon_hoc'
    id = db.Column(db.Integer, primary_key=True)
    ma_mon_hoc = db.Column(db.String(100))
    ten_mon = db.Column(db.String(100))
    so_tin_chi = db.Column(db.Integer)
    he_so_mon = db.Column(db.Float)
    # dang_ki_mon_hoc = db.relationship('DangKyMonHoc', backref='mon_hoc')


class DonViPhi(db.Model):
    __tablename__ = 'don_vi_phi'
    id = db.Column(db.Integer, primary_key=True)
    nam_hoc = db.Column(db.Integer)
    muc_phi = db.Column(db.Integer)
    # dang_ki_mon_hoc_rel = db.relationship('DangKyMonHoc', backref='don_vi_phi')


class SinhVien(db.Model):
    __tablename__ = 'sinh_vien'
    id = db.Column(db.Integer, primary_key=True)
    ma_sinh_vien = db.Column(db.String(10))
    ten_sinh_vien = db.Column(db.String(100))
    # dang_ki_mon_hoc = db.relationship('DangKyMonHoc', backref='sinh_vien')


class DangKyMonHoc(db.Model):
    __tablename__ = 'dang_ki_mon_hoc'
    id = db.Column(db.Integer, primary_key=True)
    sinh_vien_id = db.Column(db.Integer, db.ForeignKey('sinh_vien.id'), nullable=False)
    mon_hoc_id = db.Column(db.Integer, db.ForeignKey('mon_hoc.id'), nullable=False)
    hoc_ky = db.Column(db.String(20), nullable=False)
    nam_hoc_id = db.Column(db.Integer, db.ForeignKey('don_vi_phi.id'), nullable=False)
    sinh_vien = db.relationship('SinhVien', backref='dang_ki_mon_hoc')
    mon_hoc = db.relationship('MonHoc', backref='dang_ki_mon_hoc')
    don_vi_phi = db.relationship('DonViPhi', backref='dang_ki_mon_hoc')


with app.app_context():
    db.create_all()


@app.route('/lay_danh_sach_nam_hoc', methods=['GET'])
def lay_danh_sach_nam_hoc():
    try:
        nam_hoc_list = DonViPhi.query.all()
        nam_hoc_data = [{'id': nam_hoc.id, 'nam_hoc': nam_hoc.nam_hoc} for nam_hoc in nam_hoc_list]

        return jsonify({'nam_hoc_list': nam_hoc_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tạo API để thêm môn học
@app.route('/them_mon_hoc', methods=['POST'])
def create_mon_hoc():
    ma_mon_hoc = request.form.get('ma_mon_hoc')
    ten_mon = request.form.get('ten_mon')
    so_tin_chi = request.form.get('so_tin_chi')
    he_so_mon = request.form.get('he_so_mon')
    existing_mon_hoc = MonHoc.query.filter_by(ma_mon_hoc=ma_mon_hoc).first()
    if existing_mon_hoc:
        return jsonify({'error': f'Môn học {ten_mon} đã tồn tại'}), 400
    mon_hoc = MonHoc(ma_mon_hoc=ma_mon_hoc, ten_mon=ten_mon, so_tin_chi=so_tin_chi, he_so_mon=he_so_mon)
    db.session.add(mon_hoc)
    db.session.commit()

    # Trả về danh sách các môn học dưới dạng JSON
    return jsonify({'message': 'Thêm môn học thành công'}), 200

#api trả về danh sách môn học
@app.route('/lay_danh_sach_mon_hoc', methods=['GET'])
def danhsach():
    mon_hoc_list = MonHoc.query.all()
    mon_hoc_data = []
    for mon_hoc in mon_hoc_list:
        mon_hoc_data.append({
            'ma_mon_hoc': mon_hoc.ma_mon_hoc,
            'ten_mon': mon_hoc.ten_mon,
            'so_tin_chi': mon_hoc.so_tin_chi,
            'he_so_mon': mon_hoc.he_so_mon
        })
    return jsonify({'mon_hoc_list': mon_hoc_data})

# API thêm đơn vị phí
@app.route('/them_don_vi_phi', methods=['POST'])
def create_don_vi_phi():
    nam_hoc = request.form.get('nam_hoc')
    muc_phi = request.form.get('muc_phi')
    existing_don_vi_phi = DonViPhi.query.filter_by(nam_hoc=nam_hoc).first()
    if existing_don_vi_phi:
        return jsonify({'error': f'Đơn vị phí cho năm học {nam_hoc} đã tồn tại'}), 400
    don_vi_phi = DonViPhi(nam_hoc=nam_hoc, muc_phi=muc_phi)
    db.session.add(don_vi_phi)
    db.session.commit()
    return jsonify({'message': 'Đơn vị phí đã được tạo thành công'}), 201


@app.route('/them_sinh_vien', methods=['POST'])
def them_sinh_vien():
    ma_sinh_vien = request.form.get('ma_sinh_vien')
    ten_sinh_vien = request.form.get('ten_sinh_vien')
    existing_sinh_vien = SinhVien.query.filter_by(ma_sinh_vien=ma_sinh_vien).first()
    if existing_sinh_vien:
        return jsonify({'error': 'Sinh viên đã tồn tại'}), 400
    sinh_vien = SinhVien(ma_sinh_vien=ma_sinh_vien, ten_sinh_vien=ten_sinh_vien)
    db.session.add(sinh_vien)
    db.session.commit()
    return jsonify({'message': f'Sinh viên {ten_sinh_vien} đã được thêm thành công'}), 201


# API them dang ki mon hoc
@app.route('/them_dang_ki_mon_hoc', methods=['POST'])
def them_dang_ki_mon_hoc():
    try:
        with db.session.begin_nested():
            ma_sinh_vien = request.form.get('ma_sinh_vien')
            ma_mon_hoc = request.form.get('ma_mon_hoc')
            hoc_ky = request.form.get('hoc_ky')
            nam_hoc = request.form.get('nam_hoc')
            sinh_vien = SinhVien.query.filter_by(ma_sinh_vien=ma_sinh_vien).first()
            mon_hoc = MonHoc.query.filter_by(ma_mon_hoc=ma_mon_hoc).first()
            existing_mon_hoc = DangKyMonHoc.query.filter_by(mon_hoc_id=mon_hoc.id, hoc_ky=hoc_ky, sinh_vien_id=sinh_vien.id).first()
            if existing_mon_hoc:
                return jsonify({'error': 'Môn học đã tồn tại'}), 200
            if not sinh_vien or not mon_hoc:
                return jsonify({'error': 'Sinh viên hoặc môn học không tồn tại'}), 400
            don_vi_phi = DonViPhi.query.filter_by(nam_hoc=nam_hoc).first()
            if not don_vi_phi:
                return jsonify({'error': 'Năm học không tồn tại'}), 400
            dang_ki_mon_hoc = DangKyMonHoc(
                sinh_vien_id=sinh_vien.id,
                mon_hoc_id=mon_hoc.id,
                hoc_ky=hoc_ky,
                nam_hoc_id=don_vi_phi.id
            )
            db.session.add(dang_ki_mon_hoc)
            db.session.commit()
        return jsonify({'message': f'Đăng ký môn học cho sinh viên {ma_sinh_vien} đã được thêm thành công'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API trả về học phí
@app.route('/hoc_phi/<string:ma_sinh_vien>', methods=['GET'])
def tinh_hoc_phi(ma_sinh_vien):
    try:
        query_hoc_ky = request.args.get('hoc_ky')
        sinh_vien = SinhVien.query.filter_by(ma_sinh_vien=ma_sinh_vien).first()
        if not sinh_vien:
            return jsonify({'error': 'Sinh viên không tồn tại'}), 404
        existing_hoc_ki = DangKyMonHoc.query.filter_by(hoc_ky=query_hoc_ky).first()
        if not existing_hoc_ki:
            return jsonify({'error': 'Học kì không tồn tại'})
        query_nam_hoc = request.args.get('nam_hoc')
        dang_ky_mon_hoc = DangKyMonHoc.query.filter_by(sinh_vien_id=sinh_vien.id, hoc_ky=query_hoc_ky, nam_hoc_id=query_nam_hoc).all()
        hoc_phi_moi_mon = []
        tong_hoc_phi = 0.0
        for dk in dang_ky_mon_hoc:
            don_vi_phi = DonViPhi.query.filter_by(id=dk.nam_hoc_id).first()
            hoc_phi_mon_hoc = dk.mon_hoc.so_tin_chi * don_vi_phi.muc_phi * dk.mon_hoc.he_so_mon
            tong_hoc_phi += hoc_phi_mon_hoc
            nam_hoc = don_vi_phi.nam_hoc
            hoc_phi_moi_mon.append(
                {'ma_mon_hoc': dk.mon_hoc.ma_mon_hoc, 'so_tin_chi': dk.mon_hoc.so_tin_chi,'he_so_mon':dk.mon_hoc.he_so_mon
                    , 'ten_mon': dk.mon_hoc.ten_mon, 'hoc_phi': hoc_phi_mon_hoc})
        return jsonify({'ma_sinh_vien': ma_sinh_vien, 'hoc tong hoc phi': tong_hoc_phi,
                        'hoc_phi_tung_mon': hoc_phi_moi_mon, 'hoc_ky': query_hoc_ky, 'nam_hoc': nam_hoc}, ), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lấy tên môn học
@app.route('/lay_ten_mon_hoc', methods=['GET'])
def lay_ten_mon_hoc():
    ma_mon_hoc = request.args.get('ma_mon_hoc')
    mon_hoc = MonHoc.query.filter_by(ma_mon_hoc=ma_mon_hoc).first()
    if mon_hoc:
        ten_mon_hoc = mon_hoc.ten_mon  # Lấy tên môn học
        return jsonify({'ten_mon_hoc': ten_mon_hoc})
    else:
        return jsonify({'error': 'Không tìm thấy môn học'}), 404


@app.route('/danh_sach_mon_da_dang_ky/<string:ma_sinh_vien>', methods=['GET'])
def danh_sach_mon_da_dang_ky(ma_sinh_vien):
    try:
        sinh_vien = SinhVien.query.filter_by(ma_sinh_vien=ma_sinh_vien).first()
        if not sinh_vien:
            return jsonify({'error': 'Sinh viên không tồn tại'}), 404
        dang_ky_mon_hoc = DangKyMonHoc.query.filter_by(sinh_vien_id=sinh_vien.id).all()
        mon_hoc_da_dang_ky = []
        for dk in dang_ky_mon_hoc:
            mon_hoc_da_dang_ky.append({
                'ma_mon_hoc': dk.mon_hoc.ma_mon_hoc,
                'ten_mon': dk.mon_hoc.ten_mon,
                'hoc_ky': dk.hoc_ky,
                'nam_hoc': dk.don_vi_phi.nam_hoc
            })

        return jsonify({'ma_sinh_vien': ma_sinh_vien, 'danh_sach_mon_da_dang_ky': mon_hoc_da_dang_ky}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/them_mon_hoc_page')
def them_mon_hoc():
    return render_template('monhoc.html')


@app.route('/them_don_vi_phi_page')
def them_don_vi_phi_page():
    return render_template('trang.html')


@app.route('/them_sinh_vien_page')
def them_sinh_vien_page():
    return render_template('add_sinh_vien.html')


@app.route('/them_dang_ki_mon_hoc_page')
def them_dang_ki_mon_hoc_page():
    return render_template('kyhoc.html')

@app.route('/quan_ly_hoc_phi')
def quan_ly_hoc_phi():
    return render_template('hocphi.html')

if __name__ == '__main__':
    app.run(debug=True)
