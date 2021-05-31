from django.shortcuts import render, redirect
from django.db import InternalError, connection
from django.contrib import messages

# Create your views here.

def index(request):
    return render(request, "pengguna/index.html")

def login(request):
    if request.session.get("username", False):
        return redirect("pengguna:index")

    if request.method == "POST":
        found = False
        role = None

        with connection.cursor() as cursor:

            cursor.execute(f"""
                SELECT * FROM PENGGUNA
                WHERE username='{request.POST["username"]}'
                AND password='{request.POST["password"]}'
                """)

            row = cursor.fetchall()
            if (len(row) != 0): # Berhasil login
                request.session["username"] = row[0][0]
                return redirect("pengguna:index")

            else: # Gagal login
                messages.add_message(request, messages.WARNING, "Maaf, username atau password salah.")

    return render(request, "pengguna/login.html")

def logout(request):
    request.session.pop("username", None)
    return redirect("pengguna:index")

def registerSupplier(request):

    if request.method == "POST":
        with connection.cursor() as cursor:
            username = request.POST["username"]

            cursor.execute(f"""
                SELECT FROM PENGGUNA WHERE username = '{request.POST["username"]}'
            """)

            # Jika tidak terdapat username yang sama pada PENGGUNA
            if (len(cursor.fetchall())== 0):
                cursor.execute(f"""
                    INSERT INTO PENGGUNA VALUES 
                    ('{request.POST['username']}','{request.POST['password']}','{request.POST['nama']}',
                    '{request.POST['alamat_kel']}','{request.POST['alamat_kec']}','{request.POST['alamat_kabkot']}',
                    '{request.POST['alamat_prov']}','{request.POST['no_telepon']}')
                """)

                cursor.execute(f"""
                    INSERT INTO SUPPLIER VALUES
                    ('{request.POST['username']}','{request.POST['nama']}')
                """)

                messages.add_message(request,messages.SUCCESS, f"Registrasi Supplier Berhasil Dilakukan, Silahkan Login")

                return redirect("pengguna:login")
            else:
                print("SOKIN")
                messages.add_message(request, messages.WARNING, f"{request.POST['username']} sudah terdaftar sebelumnya")

    return render(request, "pengguna/RegisterSupplier.html")

def registerPetugasFaskes(request):

    if request.method == "POST":
        with connection.cursor() as cursor:
            username = request.POST["username"]

            cursor.execute(f"""
                SELECT FROM PENGGUNA WHERE username = '{request.POST["username"]}'
            """)

            # Jika tidak terdapat username yang sama pada PENGGUNA
            if (len(cursor.fetchall())== 0):
                cursor.execute(f"""
                    INSERT INTO PENGGUNA VALUES 
                    ('{request.POST['username']}','{request.POST['password']}','{request.POST['nama']}',
                    '{request.POST['alamat_kel']}','{request.POST['alamat_kec']}','{request.POST['alamat_kabkot']}',
                    '{request.POST['alamat_prov']}','{request.POST['no_telepon']}')
                """)

                cursor.execute(f"""
                    INSERT INTO PETUGAS_FASKES VALUES
                    ('{request.POST['username']}')
                """)

                messages.add_message(request,messages.SUCCESS, f"Registrasi Petugas Faskes Berhasil Dilakukan, Silahkan Login")

                return redirect("pengguna:login")
            else:
                messages.add_message(request, messages.WARNING, f"{request.POST['username']} sudah terdaftar sebelumnya")

    return render(request, "pengguna/RegisterPetugasFaskes.html")

def registerPetugasDistribusi(request):   
    if request.method == "POST":
        with connection.cursor() as cursor:
            username = request.POST["username"]

            cursor.execute(f"""
                SELECT FROM PENGGUNA WHERE username = '{request.POST["username"]}'
            """)

            # Jika tidak terdapat username yang sama pada PENGGUNA
            if (len(cursor.fetchall())== 0):
                cursor.execute(f"""
                    INSERT INTO PENGGUNA VALUES 
                    ('{request.POST['username']}','{request.POST['password']}','{request.POST['nama']}',
                    '{request.POST['alamat_kel']}','{request.POST['alamat_kec']}','{request.POST['alamat_kabkot']}',
                    '{request.POST['alamat_prov']}','{request.POST['no_telepon']}')
                """)

                cursor.execute(f"""
                    INSERT INTO PETUGAS_DISTRIBUSI VALUES
                    ('{request.POST['username']}','{request.POST['no_sim']}')
                """)

                messages.add_message(request,messages.SUCCESS, f"Registrasi Petugas Distribusi Berhasil Dilakukan, Silahkan Login")

                return redirect("pengguna:login")
            else:
                messages.add_message(request, messages.WARNING, f"{request.POST['username']} sudah terdaftar sebelumnya")

    return render(request, "pengguna/RegisterPetugasDistribusi.html")

def registerAdminSatgas(request):
    if request.method == "POST":
        with connection.cursor() as cursor:
            username = request.POST["username"]

            cursor.execute(f"""
                SELECT FROM PENGGUNA WHERE username = '{request.POST["username"]}'
            """)

            # Jika tidak terdapat username yang sama pada PENGGUNA
            if (len(cursor.fetchall())== 0):
                cursor.execute(f"""
                    INSERT INTO PENGGUNA VALUES 
                    ('{request.POST['username']}','{request.POST['password']}','{request.POST['nama']}',
                    '{request.POST['alamat_kel']}','{request.POST['alamat_kec']}','{request.POST['alamat_kabkot']}',
                    '{request.POST['alamat_prov']}','{request.POST['no_telepon']}')
                """)

                cursor.execute(f"""
                    INSERT INTO ADMIN_SATGAS VALUES
                    ('{request.POST['username']}')
                """)

                messages.add_message(request,messages.SUCCESS, f"Registrasi Admin Satgas Berhasil Dilakukan, Silahkan Login")

                return redirect("pengguna:login")
            else:
                messages.add_message(request, messages.WARNING, f"{request.POST['username']} sudah terdaftar sebelumnya")

    return render(request, "pengguna/RegisterAdminSatgas.html")