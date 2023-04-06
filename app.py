from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import pandas as pd
import mysql.connector
import xlrd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly as py
import plotly.graph_objs as go
import warnings
from sklearn.cluster import KMeans

#config database
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lusukacraft'
app.secret_key = "caircoders-ednalan-06300131"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/lusukacraft'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True

# Database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="lusukacraft"
)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)
mysql = MySQL(app)

class Login(FlaskForm):
	username = StringField('', validators=[InputRequired() ], render_kw={'autofocus':True, 'placeholder': 'Username'})
	password = PasswordField('', validators=[InputRequired() ], render_kw={'autofocus':True, 'placeholder': 'Password'})

class admin(db.Model):
	__tablename__ = 'admin'
	idAdmin = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20))
	password = db.Column(db.Text)
	nama = db.Column(db.String(50))
	email = db.Column(db.String(50))

	def __init__(self,username,password,nama,email) :
		self.username = username
		if password != '' :
			self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
		self.nama = nama
		self.email = email

class penjualan(db.Model):
	__tablename__ = 'penjualan'
	noPesanan = db.Column(db.String(20), primary_key=True) #perlu diganti biar ga primarykey
	statusPesanan = db.Column(db.String(7))
	alasanPembatalan = db.Column(db.String(50), nullable=True)
	statusPembatalan = db.Column(db.String(20), nullable=True)
	noResi = db.Column(db.String(20), nullable=True)
	opsiPengiriman = db.Column(db.Text, nullable=True)
	antarPengiriman = db.Column(db.Text, nullable=True)
	waktuPengirimanDiatur = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
	waktuPesananDibuat = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
	waktuPesananDilakukan = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
	namaProduk = db.Column(db.String(250), nullable=True)
	namaVariasi = db.Column(db.String(250), nullable=True)
	harga = db.Column(db.Integer)
	jumlah = db.Column(db.Integer)
	totalHarga = db.Column(db.Integer)
	beratProduk = db.Column(db.Integer)
	ongkosKirim = db.Column(db.Integer)
	usernamePembeli = db.Column(db.String(50))
	namaPenerima = db.Column(db.String(200))
	noTelepon = db.Column(db.String(20))
	alamatPengiriman = db.Column(db.Text)
	kabupaten = db.Column(db.String(70))
	provinsi = db.Column(db.String(50))
	waktuPesananSelesai = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), nullable=True)

	def __init__(self,noPesanan,statusPesanan,alasanPembatalan,statusPembatalan,noResi,opsiPengiriman,antarPengiriman,waktuPengirimanDiatur,waktuPesananDibuat,waktuPesananDilakukan,namaProduk,namaVariasi, harga,jumlah,totalHarga,beratProduk,ongkosKirim,usernamePembeli,namaPenerima,noTelepon,alamatPengiriman,kabupaten,provinsi,waktuPesananSelesai) :
		self.noPesanan = noPesanan
		self.statusPesanan = statusPesanan
		self.alasanPembatalan = alasanPembatalan
		self.statusPembatalan = statusPembatalan
		self.noResi = noResi
		self.opsiPengiriman = opsiPengiriman
		self.antarPengiriman = antarPengiriman
		self.waktuPengirimanDiatur = waktuPengirimanDiatur
		self.waktuPesananDibuat = waktuPesananDibuat
		self.waktuPesananDilakukan = waktuPesananDilakukan
		self.namaProduk = namaProduk
		self.namaVariasi = namaVariasi
		self.harga = harga
		self.jumlah = jumlah
		self.totalHarga = totalHarga
		self.beratProduk = beratProduk
		self.ongkosKirim = ongkosKirim
		self.usernamePembeli = usernamePembeli
		self.namaPenerima = namaPenerima
		self.noTelepon = noTelepon
		self.alamatPengiriman = alamatPengiriman
		self.kabupaten = kabupaten
		self.provinsi = provinsi
		self.waktuPesananSelesai = waktuPesananSelesai

		

#app.app_context().push() --? 
#mengatasi error tidak berjalan pada environment yang sama
with app.app_context():
	db.create_all()


def login_dulu(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'login' in session:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('login'))
	return wrap

@app.route('/')
def index():
	if session.get('login')==True:
		return redirect(url_for('dashboard'))
	return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	if session.get('login')==True:
		return redirect(url_for('dashboard'))
	form = Login()
	if form.validate_on_submit():
		user = admin.query.filter_by(username=form.username.data).first()
		if user:
			if bcrypt.check_password_hash(user.password, form.password.data):
				session['login'] = True
				session['id'] = user.idAdmin
				return redirect(url_for('dashboard'))
		pesan = "Username atau Password Anda Salah"
		return render_template("login.html", pesan=pesan, form=form)
	return render_template('login.html', form=form)

@app.route('/dashboard')
@login_dulu
def dashboard():
	#data1 = db.session.query(func.sum(penjualan.totalHarga)).scalar()
	#data1 = db.session.execute("SELECT CONCAT('Rp ',FORMAT(SUM(totalHarga),2,'id_ID')) from penjualan").scalars()
	cur1 = mysql.connection.cursor()
	cur1.execute("SELECT CONCAT('Rp ',FORMAT(SUM(totalHarga),2,'id_ID')) FROM penjualan WHERE statusPesanan='Selesai'")
	totalpendapatan = cur1.fetchone()
	cur1.close()
	totalpendapatan1 = totalpendapatan
	delimiter = ','
	totalpendapatan2 = delimiter.join([str(totalpendapatan1) for totalpendapatan1 in totalpendapatan])

	cur2 = mysql.connection.cursor()
	cur2.execute("SELECT COUNT(DISTINCT noPesanan) FROM penjualan WHERE statusPesanan='Selesai'")
	totalpenjualan = cur2.fetchone()
	cur2.close()
	totalpenjualan1 = totalpenjualan
	delimiter = ','
	totalpenjualan2 = delimiter.join([str(totalpenjualan1) for totalpenjualan1 in totalpenjualan])

	cur3 = mysql.connection.cursor()
	cur3.execute("SELECT COUNT(DISTINCT usernamePembeli) FROM penjualan WHERE statusPesanan='Selesai'")
	totalpelanggan = cur3.fetchone()
	cur3.close()
	totalpelanggan1 = totalpelanggan
	delimiter = ','
	totalpelanggan2 = delimiter.join([str(totalpelanggan1) for totalpelanggan1 in totalpelanggan])

	cur4 = mysql.connection.cursor()
	cur4.execute("SELECT COUNT(DISTINCT namaProduk) FROM penjualan")
	totalproduk = cur4.fetchone()
	cur4.close()
	totalproduk1 = totalproduk
	delimiter = ','
	totalproduk2 = delimiter.join([str(totalproduk1) for totalproduk1 in totalproduk])

	cur5 = mysql.connection.cursor()
	cur5.execute("select cast(sum(totalHarga) as INT) from penjualan where waktuPesananSelesai > '2022-12-14' - INTERVAL 5 month group by month(waktuPesananSelesai)")
	revenue5bulan = cur5.fetchall()
	cur5.close()
	revenue5bulan1 = [i[0] for i in revenue5bulan]
	
	cur6 = mysql.connection.cursor()
	cur6.execute("SELECT usernamePembeli, CONCAT('Rp ',FORMAT(SUM(totalHarga),2,'id_ID')), SUM(totalHarga) AS jumlahterbanyak from penjualan WHERE statusPesanan='Selesai' group by usernamePembeli ORDER BY jumlahterbanyak DESC LIMIT 5")
	toptotalharga = cur6.fetchall()
	cur6.close()

	cur7 = mysql.connection.cursor()
	cur7.execute("SELECT usernamePembeli, COUNT(DISTINCT(noPesanan)) AS jumlahterbanyak from penjualan WHERE statusPesanan='Selesai' group by usernamePembeli ORDER BY jumlahterbanyak desc LIMIT 5")
	toptotalbeli = cur7.fetchall()
	cur7.close()

	cur8 = mysql.connection.cursor()
	cur8.execute("SELECT opsiPengiriman, COUNT(opsiPengiriman) AS opsiterbanyak from penjualan WHERE statusPesanan='Selesai' group by opsiPengiriman ORDER BY opsiterbanyak desc LIMIT 5")
	toppengiriman = cur8.fetchall()
	cur8.close()

	return render_template('/dashboard.html', data1=totalpendapatan2, data2=totalpenjualan2, data3=totalpelanggan2, data4=totalproduk2, data5=revenue5bulan1, data6=toptotalharga, data7=toptotalbeli, data8=toppengiriman)

@app.route('/dashboardpelanggan')
@login_dulu
def dashboardpelanggan():
	cur1 = mysql.connection.cursor()
	cur1.execute("SELECT COUNT(DISTINCT usernamePembeli) FROM penjualan WHERE statusPesanan='Selesai'")
	totalpelanggan = cur1.fetchone()
	cur1.close()
	totalpelanggan1 = totalpelanggan
	delimiter = ','
	totalpelanggan2 = delimiter.join([str(totalpelanggan1) for totalpelanggan1 in totalpelanggan])

	cur2 = mysql.connection.cursor()
	cur2.execute("SELECT COUNT(DISTINCT noPesanan) FROM penjualan WHERE statusPesanan='Selesai'")
	totalpenjualan = cur2.fetchone()
	cur2.close()
	totalpenjualan1 = totalpenjualan
	delimiter = ','
	totalpenjualan2 = delimiter.join([str(totalpenjualan1) for totalpenjualan1 in totalpenjualan])

	cur3 = mysql.connection.cursor()
	cur3.execute("SELECT COUNT(DISTINCT kabupaten) FROM penjualan WHERE statusPesanan='Selesai'")
	totalkabupaten = cur3.fetchone()
	cur3.close()
	totalkabupaten1 = totalkabupaten
	delimiter = ','
	totalkabupaten2 = delimiter.join([str(totalkabupaten1) for totalkabupaten1 in totalkabupaten])

	cur4 = mysql.connection.cursor()
	cur4.execute("SELECT COUNT(DISTINCT provinsi) FROM penjualan WHERE statusPesanan='Selesai'")
	totalprovinsi = cur4.fetchone()
	cur4.close()
	totalprovinsi1 = totalprovinsi
	delimiter = ','
	totalprovinsi2 = delimiter.join([str(totalprovinsi1) for totalprovinsi1 in totalprovinsi])

	cur5 = mysql.connection.cursor()
	cur5.execute("SELECT usernamePembeli, CONCAT('Rp ',FORMAT(SUM(totalHarga),2,'id_ID')), SUM(totalHarga) AS jumlahterbanyak, COUNT(DISTINCT(noPesanan)) AS banyakbeli, max(namaProduk) from penjualan WHERE statusPesanan='Selesai' group by usernamePembeli ORDER BY jumlahterbanyak DESC LIMIT 10")
	pelangganbeli = cur5.fetchall()
	cur5.close()

	return render_template('/dashboardpelanggan.html', data1=totalpelanggan2, data2=totalpenjualan2, data3=totalkabupaten2, data4=totalprovinsi2, data5=pelangganbeli)

@app.route('/dashboardproduk')
@login_dulu
def dashboardproduk():
	cur1 = mysql.connection.cursor()
	cur1.execute("SELECT COUNT(DISTINCT namaProduk) FROM penjualan")
	totalproduk = cur1.fetchone()
	cur1.close()
	totalproduk1 = totalproduk
	delimiter = ','
	totalproduk2 = delimiter.join([str(totalproduk1) for totalproduk1 in totalproduk])

	cur2 = mysql.connection.cursor()
	cur2.execute("SELECT SUM(jumlah) FROM penjualan WHERE statusPesanan='Selesai'")
	totalprodukterjual = cur2.fetchone()
	cur2.close()
	totalprodukterjual1 = totalprodukterjual
	delimiter = ','
	totalprodukterjual2 = delimiter.join([str(totalprodukterjual1) for totalprodukterjual1 in totalprodukterjual])

	cur3 = mysql.connection.cursor()
	cur3.execute("SELECT namaProduk, COUNT(namaProduk) AS jumlahterbanyak from penjualan WHERE statusPesanan='Selesai' group by namaProduk ORDER BY jumlahterbanyak desc LIMIT 10")
	topproduk = cur3.fetchall()
	cur3.close()

	cur4 = mysql.connection.cursor()
	cur4.execute("SELECT namaProduk, COUNT(namaProduk) AS jumlahterbanyak from penjualan WHERE statusPesanan='Selesai' group by namaProduk ORDER BY jumlahterbanyak desc LIMIT 10")
	hotproduk = cur4.fetchall()
	cur4.close()

	cur5 = mysql.connection.cursor()
	cur5.execute("SELECT namaProduk, CONCAT('Rp ',FORMAT(harga,0,'id_ID')), SUM(jumlah) AS bestseller from penjualan WHERE statusPesanan='Selesai' group by namaProduk ORDER BY bestseller desc LIMIT 10")
	bestseller = cur5.fetchall()
	cur5.close()

	return render_template('/dashboardproduk.html', data1=totalproduk2, data2=totalprodukterjual2, data3=topproduk, data4=hotproduk, data5=bestseller)

def datapelanggan():
	cur = mysql.connection.cursor()
	cur.execute("SELECT usernamePembeli, alamatPengiriman, kabupaten, provinsi FROM penjualan GROUP BY usernamePembeli")
	pelanggan = cur.fetchall()
	cur.close()
	return render_template('/datapelanggan.html', menu='data', submenu='pelanggan', data=pelanggan)

@app.route('/dataadmin')
@login_dulu
def dataadmin():
	data = admin.query.all()
	return render_template('/dataadmin.html', data=data, menu='data', submenu='admin')

@app.route('/tambahdataadmin', methods=['GET', 'POST'])
@login_dulu
def tambahdataadmin():
	if request.method == "POST":
		username = request.form['username']
		password = request.form['password']
		nama = request.form['nama']
		email = request.form['email']
		db.session.add(admin(username,password,nama,email))
		db.session.commit()
		return redirect(url_for('dataadmin'))

@app.route('/editdataadmin/<idAdmin>', methods=['GET', 'POST'])
@login_dulu
def editdataadmin(idAdmin):
	data = admin.query.filter_by(idAdmin=idAdmin).first()
	if request.method == "POST":
		try:
			data.username = request.form['username']
			if data.password != '':
				data.password = bcrypt.generate_password_hash(request.form['password']).decode('UTF-8')
			data.nama = request.form['nama']
			data.email = request.form['email']
			db.session.add(data)
			db.session.commit()
			return redirect(url_for('dataadmin'))
		except:
			flash("Terdapat Trouble")
			return redirect(request.referrer)
		
@app.route('/hapusdataadmin/<idAdmin>', methods=['GET', 'POST'])
@login_dulu
def hapusdataadmin(idAdmin):
	data = admin.query.filter_by(idAdmin=idAdmin).first()
	db.session.delete(data)
	db.session.commit()
	return redirect(url_for('dataadmin'))


@app.route('/datapelanggan')
@login_dulu
def datapelanggan():
	cur = mysql.connection.cursor()
	cur.execute("SELECT usernamePembeli, alamatPengiriman, kabupaten, provinsi FROM penjualan GROUP BY usernamePembeli ORDER BY usernamePembeli ASC")
	pelanggan = cur.fetchall()
	cur.close()
	return render_template('/datapelanggan.html', menu='data', submenu='pelanggan', data=pelanggan)

@app.route('/databarang')
@login_dulu
def databarang():
	cur = mysql.connection.cursor()
	cur.execute("SELECT namaProduk, namaVariasi, CONCAT('Rp ',FORMAT(harga,0,'id_ID')) FROM penjualan GROUP BY namaProduk")
	barang = cur.fetchall()
	cur.close()
	return render_template('/databarang.html', menu='data', submenu='barang', data=barang)

@app.route('/formtransaksi')
@login_dulu
def formtransaksi():
	#data = admin.query.all()
	return render_template('/formtransaksi.html', menu='transaksi', submenu='form')

mycursor = mydb.cursor(buffered=True)
mycursor.execute("SHOW DATABASES")

@app.route('/datatransaksi')
@login_dulu
def datatransaksi():
	cur = mysql.connection.cursor()
	cur.execute("select noPesanan, statusPesanan, alasanPembatalan, statusPembatalan, noResi ,opsiPengiriman, antarPengiriman, waktuPengirimanDiatur, waktuPesananDibuat, waktuPesananDilakukan, namaProduk, namaVariasi, CONCAT('Rp ',FORMAT(harga,0,'id_ID')), jumlah, CONCAT('Rp ',FORMAT(totalHarga,0,'id_ID')), beratProduk, ongkosKirim, usernamePembeli, namaPenerima, noTelepon, alamatPengiriman, CONCAT(kabupaten, ', ' , provinsi), waktuPesananSelesai from penjualan where waktuPesananSelesai> now() - INTERVAL 8 month ORDER BY waktuPesananSelesai DESC")
	transaksi = cur.fetchall()
	cur.close()
	return render_template('/datatransaksi.html', menu='transaksi', submenu='data', data=transaksi)


# Get the uploaded files
UPLOAD_FOLDER_EXCEL = 'static/excel'
app.config['UPLOAD_FOLDER_EXCEL'] = UPLOAD_FOLDER_EXCEL
ALLOWED_EXTENSIONS_EXCEL = set(['csv', 'xls', 'xlsx'])
def allowed_file_excel(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_EXCEL

@app.route("/simpanformpenjualan_excel", methods=["POST","GET"])
@login_dulu
def simpanformpenjualan_excel():
	conn = mysql.connection.cursor()
	if request.method == 'POST':
		file = request.files['file']
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER_EXCEL'], filename))
		namefile = "C:/xampp/htdocs/lusukacraft/static/excel/"+filename
		excel = xlrd.open_workbook(namefile)
		sheet = excel.sheet_by_index(0)
		jum_row = sheet.nrows
		for baris in range(jum_row):
			if baris == 0: continue
			else:
				sql = "INSERT INTO `penjualan`(`noPesanan`, `statusPesanan`, `alasanPembatalan`, `statusPembatalan`,`noResi`,`opsiPengiriman`, `antarPengiriman`,`waktuPengirimanDiatur`,`waktuPesananDibuat`,`waktuPesananDilakukan`,`namaProduk`,`namaVariasi`,`harga`, `jumlah`, `totalHarga`,`beratProduk`,`ongkosKirim`, `usernamePembeli`,`namaPenerima`,`noTelepon`,`alamatPengiriman`,`kabupaten`,`provinsi`,`waktuPesananSelesai`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
				val = tuple(sheet.row_values(baris))
				conn.execute(sql, val)
				mysql.connection.commit()
	flash('Berhasil Masuk')
	conn.close()
	return redirect(url_for('datatransaksi'))

@app.route('/detailsdatatransaksi/<noPesanan>', methods=['GET', 'POST'])
@login_dulu
def detailsdatatransaksi(noPesanan):
	data = penjualan.query.filter_by(noPesanan=noPesanan).first()
	if request.method == "POST":
		try:
			data.noPesanan = request.form['noPesanan']
			data.statusPesanan = request.form['statusPesanan']
			data.alasanPembatalan = request.form['alasanPembatalan']
			data.statusPembatalan = request.form['statusPembatalan']
			data.noResi = request.form['noResi']
			data.opsiPengiriman = request.form['opsiPengiriman']
			data.antarPengiriman = request.form['antarPengiriman']
			data.waktuPengirimanDiatur = request.form['waktuPengirimanDiatur']
			data.waktuPesananDibuat = request.form['waktuPesananDibuat']
			data.waktuPesananDilakukan = request.form['waktuPesananDilakukan']
			data.namaProduk = request.form['namaProduk']
			data.namaVariasi = request.form['namaVariasi']
			data.harga = request.form['harga']
			data.jumlah = request.form['jumlah']
			data.totalHarga = request.form['totalHarga']
			data.beratProduk = request.form['beratProduk']
			data.ongkosKirim = request.form['ongkosKirim']
			data.usernamePembeli = request.form['usernamePembeli']
			data.namaPenerima = request.form['namaPenerima']
			data.noTelepon = request.form['noTelepon']
			data.alamatPengiriman = request.form['alamatPengiriman']
			data.kabupaten = request.form['kabupaten']
			data.provinsi = request.form['provinsi']
			data.waktuPesananSelesai = request.form['waktuPesananSelesai']
			db.session.view(data)
			db.session.commit()
			return redirect(url_for('datatransaksi'))
		except:
			flash("Terdapat Trouble")
			return redirect(request.referrer)

@app.route('/hasillrfmp')
@login_dulu
def hasillrfmp():
	cur = mysql.connection.cursor()
	cur.execute("WITH ptttt1 AS(WITH pttt1 AS (WITH ptt1 AS (WITH pt1 AS (SELECT p1.noPesanan, p1.usernamePembeli, p1.waktuPesananSelesai, row_number() OVER( PARTITION BY p1.noPesanan ORDER BY p1.noPesanan) AS row_num FROM penjualan p1 WHERE p1.statusPesanan = 'Selesai') SELECT *, row_number() OVER(PARTITION BY pt1.usernamePembeli ORDER BY pt1.usernamePembeli) AS row_num2 FROM pt1) SELECT ptt1.usernamePembeli, ABS(timestampdiff(day, ptt1.waktuPesananSelesai, ptt2.waktuPesananSelesai)) AS ivt FROM ptt1 ptt1 JOIN ptt1 ptt2 ON ptt1.usernamePembeli = ptt2.usernamePembeli) SELECT pttt1.usernamePembeli, AVG(pttt1.ivt) average, STDDEV(pttt1.ivt) std_dev FROM pttt1 GROUP BY pttt1.usernamePembeli) SELECT p.usernamePembeli as Pelanggan, timestampdiff(day, min(p.waktuPesananSelesai), CURRENT_DATE) as Length, timestampdiff(day, max(p.waktuPesananSelesai), CURRENT_DATE) as Recency, COUNT(p.noPesanan) as Frequency, CONCAT('Rp. ', format((CONVERT(SUM(totalHarga), INT)), 0, 'de_De')) as Monetary, ptttt1.std_dev FROM penjualan p JOIN ptttt1 on ptttt1.usernamePembeli = p.usernamePembeli WHERE p.statusPesanan = 'Selesai' GROUP BY p.usernamePembeli")
	data = pd.DataFrame(cur.fetchall(), columns=['pelanggan', 'length', 'recency', 'frequency', 'monetary', 'periodicity'])
	data = tuple(data.itertuples(index=False, name=None))
	cur.close()
	return render_template('/hasillrfmp.html', menu='hasil', submenu='lrfmp', data=data)

@app.route('/hasilsegmentasi')
@login_dulu
def hasilsegmentasi():

	cur = mydb.cursor()
	cur.execute("WITH ptttt1 AS(WITH pttt1 AS (WITH ptt1 AS (WITH pt1 AS (SELECT p1.noPesanan, p1.usernamePembeli, p1.waktuPesananSelesai, row_number() OVER( PARTITION BY p1.noPesanan ORDER BY p1.noPesanan) AS row_num FROM penjualan p1 WHERE p1.statusPesanan = 'Selesai') SELECT *, row_number() OVER(PARTITION BY pt1.usernamePembeli ORDER BY pt1.usernamePembeli) AS row_num2 FROM pt1) SELECT ptt1.usernamePembeli, ABS(timestampdiff(day, ptt1.waktuPesananSelesai, ptt2.waktuPesananSelesai)) AS ivt FROM ptt1 ptt1 JOIN ptt1 ptt2 ON ptt1.usernamePembeli = ptt2.usernamePembeli) SELECT pttt1.usernamePembeli, AVG(pttt1.ivt) average, STDDEV(pttt1.ivt) std_dev FROM pttt1 GROUP BY pttt1.usernamePembeli) SELECT p.usernamePembeli as Pelanggan, timestampdiff(day, min(p.waktuPesananSelesai), CURRENT_DATE) as Length, timestampdiff(day, max(p.waktuPesananSelesai), CURRENT_DATE) as Recency, COUNT(p.noPesanan) as Frequency, SUM(p.totalHarga) as Monetary, ptttt1.std_dev FROM penjualan p JOIN ptttt1 on ptttt1.usernamePembeli = p.usernamePembeli WHERE p.statusPesanan = 'Selesai' GROUP BY p.usernamePembeli")
	df = pd.DataFrame(cur.fetchall(), columns=['pelanggan', 'length', 'recency', 'frequency', 'monetary', 'periodicity'])
	cur.close()

	def length_nor(row):
		l = ((row['length']-min(df['length']))/(max(df['length'])-min(df['length'])))*(1-0)+0
		return l
	def recency_nor(row):
		r = ((row['recency']-min(df['recency']))/(max(df['recency'])-min(df['recency'])))*(1-0)+0
		return r
	def frequency_nor(row):
		f = ((row['frequency']-min(df['frequency']))/(max(df['frequency'])-min(df['frequency'])))*(1-0)+0
		return f
	def monetary_nor(row):
		m = ((row['monetary']-min(df['monetary']))/(max(df['monetary' ])-min(df['monetary'])))*(1-0)+0
		return m
	def periodicity_nor(row):
		p = ((row['periodicity']-min(df['periodicity']))/(max(df['periodicity'])-min(df['periodicity'])))*(1-0)+0
		return p
    
	df['length_nor'] = df.apply(lambda row: length_nor(row), axis=1)
	df['recency_nor'] = df.apply(lambda row: recency_nor(row), axis=1)
	df['frequency_nor'] = df.apply(lambda row: frequency_nor(row), axis=1)
	df['monetary_nor'] = df.apply(lambda row: monetary_nor(row), axis=1)
	df['periodicity_nor'] = df.apply(lambda row: periodicity_nor(row), axis=1)

	warnings.filterwarnings("ignore")
	
	z = df.iloc[:,[6,7,8,9,10]].values
	selected_cols = ["pelanggan","length_nor","recency_nor","frequency_nor","monetary_nor","periodicity_nor"]
	cluster_data = df.loc[:, selected_cols]
	kmeans_s = KMeans(n_clusters=3, random_state=0).fit(z)
	label = pd.DataFrame(kmeans_s.labels_)
	clustered_data = cluster_data.assign(cluster=label)
	clustered_data = round(clustered_data, 6)
	clustered = tuple(clustered_data.itertuples(index=False, name=None))
	
	cluster_0 = clustered_data[clustered_data['cluster']==0]['pelanggan'].count()
	cluster_1 = clustered_data[clustered_data['cluster']==1]['pelanggan'].count()
	cluster_2 = clustered_data[clustered_data['cluster']==2]['pelanggan'].count()
	data_cluster = [cluster_0, cluster_1, cluster_2]

	grouped_km = clustered_data.groupby(['cluster']).mean().round(1)
	grouped_km2 = clustered_data.groupby(['cluster']).mean().round(1).reset_index()
	grouped_km2['cluster'] = grouped_km2['cluster'].map(str)
	grouped_km2 = tuple(grouped_km2.itertuples(index=False, name=None))

	return render_template('/hasilsegmentasi.html', menu='hasil', submenu='segmen',clustered=clustered, clustered_data=clustered_data, data_cluster=data_cluster, grouped_km2=grouped_km2)

@app.route('/logout')
@login_dulu
def logout():
	session.clear()
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug = True)