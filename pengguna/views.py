from django.shortcuts import render, redirect
from django.db import connection
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
