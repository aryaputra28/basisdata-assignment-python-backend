from django.shortcuts import render, redirect
from django.db import InternalError, connection
from django.contrib import messages
from datetime import date

# Create your views here.

pesanan_query = []
def createPesananSD(request):
    if request.method == "POST" and request.POST['tombol'] == "choose" :
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode
            FROM ITEM_SUMBER_DAYA
            WHERE username_supplier='{request.POST["supplier"]}'
            """)
            row = cursor.fetchall()
            kodeBarang = []
            for i in row:
                kodeBarang.append(i[0])
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT username_supplier
            FROM ITEM_SUMBER_DAYA
            """)
            row = cursor.fetchall()
            result = []
            for i in row:
                result.append(i[0])

        context = {
            "supp":request.POST['supplier'],
            "kodeBarang":kodeBarang,
            "result": result,
            "pesanan_query": pesanan_query
        }
    elif request.method == "POST" and request.POST['tombol'] == "tambah":
        # Mengambil seluruh kode barang yg dimiliki supplier
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode
            FROM ITEM_SUMBER_DAYA
            WHERE username_supplier='{request.POST["supplier"]}'
            """)
            row = cursor.fetchall()
            kodeBarang = []
            for i in row:
                kodeBarang.append(i[0])

        # Mengambil seluruh username yang menyediakan item sumber daya
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT username_supplier
            FROM ITEM_SUMBER_DAYA
            """)
            row = cursor.fetchall()
            result = []
            for i in row:
                result.append(i[0])

        # Mengambil nama item berdasarkan kode
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT nama,harga_satuan,username_supplier
            FROM item_sumber_daya
            WHERE kode='{request.POST['kode']}'
            """)
            row = cursor.fetchall()
            
            pesanan_query.append(tuple((len(pesanan_query)+1,row[0][0],row[0][1],request.POST['jumlahBarang'],row[0][2])))
        context = {
            "supp":request.POST['supplier'],
            "kodeBarang":kodeBarang,
            "result": result,
            "pesanan_query": pesanan_query
        }
    elif request.method == "POST" and request.POST['tombol'] == "simpan" :
        # Insert into transaksi_sumber_daya
        today = date.today()
        with connection.cursor() as cursor:
            cursor.execute(f"""
            INSERT INTO TRANSAKSI_SUMBER_DAYA 
            (tanggal,total_berat,total_item) VALUES 
            ('{today}',0.0,0.0)
            """)

        # Take max number from transaksi_sumber_daya
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT MAX(nomor)
            FROM transaksi_sumber_daya
            """)
            maxNumber = cursor.fetchall()

        # Insert Into pesanan_sumber_daya
        with connection.cursor() as cursor:
            cursor.execute(f"""
            INSERT INTO PESANAN_SUMBER_DAYA VALUES
            ('{maxNumber[0][0]}','{request.POST['username']}',0.0)
            """)

        # Insert Into Daftar_Item
        for i in pesanan_query:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                SELECT kode 
                FROM ITEM_SUMBER_DAYA
                WHERE nama='{i[1]}'
                """)
                kode = cursor.fetchall()
            with connection.cursor() as cursor:
                cursor.execute(f"""
                INSERT INTO DAFTAR_ITEM VALUES
                ('{maxNumber[0][0]}',{i[0]},{i[3]},{kode[0][0]},0.0,0.0)
                """)
        dataSupplier = []
        for i in pesanan_query:
            dataSupplier.append(i[4])
        dataSupplier2 = list(set(dataSupplier))
        for i in dataSupplier2:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                INSERT INTO RIWAYAT_STATUS_PESANAN VALUES
                ('REQ-SUP','{maxNumber[0][0]}','{i}','{date.today()}')
                """)
        pesanan_query.clear()

        return redirect("trigger3:ReadPesananSumberDaya")

    # Untuk delete
    elif request.method=="POST" and request.POST['tombol'] != "simpan" and request.POST['tombol'] != "tambah" and request.POST['tombol'] != "choose":
        index = int(request.POST['tombol'])-1
        del pesanan_query[index]

        for i in range(index,len(pesanan_query)):
            dataBaru = (str(i+1),pesanan_query[i][1],pesanan_query[i][2],pesanan_query[i][3])
            pesanan_query[i] = dataBaru
        
        # Mengambil seluruh kode barang yg dimiliki supplier
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode
            FROM ITEM_SUMBER_DAYA
            WHERE username_supplier='{request.POST["supplier"]}'
            """)
            row = cursor.fetchall()
            kodeBarang = []
            for i in row:
                kodeBarang.append(i[0])

        # Mengambil seluruh username yang menyediakan item sumber daya
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT username_supplier
            FROM ITEM_SUMBER_DAYA
            """)
            row = cursor.fetchall()
            result = []
            for i in row:
                result.append(i[0])
        context = {
            "supp":request.POST['supplier'],
            "kodeBarang":kodeBarang,
            "result": result,
            "pesanan_query": pesanan_query
        }
    else:
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT username_supplier
            FROM ITEM_SUMBER_DAYA
            """)
            row = cursor.fetchall()
            result = []
            for i in row:
                result.append(i[0])
            context = {
                "result": result,
            }

    return render(request, 'trigger3/CreatePesananSumberDaya.html',context)

def readPesanan(request):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT DISTINCT TSD.nomor, TSD.tanggal, TSD.total_berat, TSD.total_item, PSD.total_harga
        FROM TRANSAKSI_SUMBER_DAYA TSD, PESANAN_SUMBER_DAYA PSD, RIWAYAT_STATUS_PESANAN RSD
        WHERE PSD.nomor_pesanan=TSD.nomor and PSD.nomor_pesanan = RSD.no_pesanan and 
        PSD.username_admin_satgas='{request.session["username"]}';
        """)
        dataPertama = cursor.fetchall()
        print(dataPertama)
    dataStatus = []
    for i in dataPertama:
        print(i[0])
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT username_supplier 
            FROM riwayat_status_pesanan 
            WHERE no_pesanan = '{i[0]}';
            """)
            row = cursor.fetchall()
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode_status_pesanan 
            FROM RIWAYAT_STATUS_PESANAN
            WHERE username_supplier='{row[0][0]}' and no_pesanan = '{i[0]}';
            """)
            row = cursor.fetchall()
            dataStatus.append(row[-1][0])
    result = []
    for i in range(len(dataPertama)):
        hasil = (dataPertama[i][0],dataPertama[i][1],dataPertama[i][2],dataPertama[i][3],dataPertama[i][4],dataStatus[i])
        result.append(hasil)
    context = {
        "result":result
    }
    if request.method=="POST":
        print(request.POST['tombol'])
        with connection.cursor() as cursor:
            cursor.execute(f"""
            DELETE FROM RIWAYAT_STATUS_PESANAN 
            WHERE no_pesanan={request.POST['tombol']}
            """)
        with connection.cursor() as cursor:
            cursor.execute(f"""
            DELETE FROM PESANAN_SUMBER_DAYA
            WHERE nomor_pesanan={request.POST['tombol']}
            """)
        with connection.cursor() as cursor:
            cursor.execute(f"""
            DELETE FROM DAFTAR_ITEM
            WHERE  no_transaksi_sumber_daya={request.POST['tombol']}
            """)
        with connection.cursor() as cursor:
            cursor.execute(f"""
            DELETE FROM TRANSAKSI_SUMBER_DAYA
            WHERE nomor={request.POST['tombol']}
            """)
        return redirect("trigger3:ReadPesananSumberDaya")
        
    return render(request, 'trigger3/ReadPesananSumberDaya.html',context)
    
def detailPesanan(request,idPesanan):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT TSD.tanggal, PSD.total_harga,DI.no_urut, DI.kode_item_sumber_daya, DI.jumlah_item
        FROM TRANSAKSI_SUMBER_DAYA TSD, DAFTAR_ITEM DI, PESANAN_SUMBER_DAYA PSD
        WHERE PSD.nomor_pesanan = TSD.nomor and TSD.nomor = DI.no_transaksi_sumber_daya AND
        PSD.nomor_pesanan={idPesanan};
        """)
        dataPertama = cursor.fetchall()

    dataKedua = []
    for i in dataPertama:
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT ISD.username_supplier,ISD.nama, ISD.harga_satuan
            FROM ITEM_SUMBER_DAYA ISD, DAFTAR_ITEM DI
            WHERE DI.kode_item_sumber_daya = ISD.kode and DI.kode_item_sumber_daya='{i[3]}';
            """)
            result = cursor.fetchall()
            dataKedua.append(result[0])
    result =[]
    for i in range(len(dataPertama)):
        setup = (dataPertama[i][0],dataPertama[i][2],dataKedua[i][1],dataKedua[i][0],dataKedua[i][2],dataPertama[i][4],dataPertama[i][1])
        result.append(setup)
    context = {
        "idPesanan":idPesanan,
        "result":result
    }

    return render(request, 'trigger3/DetailPesanan.html',context)

def riwayatStatus(request,idPesanan):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT RSP.kode_status_pesanan ,SP.nama,RSP.username_supplier,RSP.tanggal
        FROM RIWAYAT_STATUS_PESANAN RSP, STATUS_PESANAN SP
        WHERE RSP.kode_status_pesanan = SP.kode and RSP.no_pesanan={idPesanan};
        """)
        row = cursor.fetchall()
    timeSort = []
    for i in reversed(row):
        timeSort.append(i)
    context = {
        "result":timeSort,
        "id":idPesanan
    }
    return render(request,'trigger3/RiwayatStatus.html',context)

pesananUpdate = []
def updatePesanan(request,idPesanan):
    if request.method == "POST" and request.POST['tombol'] == "choose":
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode
            FROM ITEM_SUMBER_DAYA
            WHERE username_supplier='{request.POST["supplier"]}'
            """)
            row = cursor.fetchall()
            kodeBarang = []
            for i in row:
                kodeBarang.append(i[0])
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT ISD.username_supplier 
            FROM ITEM_SUMBER_DAYA ISD, DAFTAR_ITEM DI
            WHERE DI.kode_item_sumber_daya = ISD.kode and no_transaksi_sumber_daya = {idPesanan};
            """)
            row = cursor.fetchall()
            allSupplier = []
            for i in row:
                allSupplier.append(i[0])

        context = {
            "id":idPesanan,
            "supp":request.POST['supplier'],
            "kodeBarang":kodeBarang,
            "allSupplier": allSupplier,
            "pesanan_query": pesananUpdate
        }
    elif request.method == "POST" and request.POST['tombol'] == "tambah":
        # Mengambil seluruh kode barang yg dimiliki supplier
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode
            FROM ITEM_SUMBER_DAYA
            WHERE username_supplier='{request.POST["supplier"]}'
            """)
            row = cursor.fetchall()
            kodeBarang = []
            for i in row:
                kodeBarang.append(i[0])

        # Mengambil seluruh username yang menyediakan item sumber daya
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT ISD.username_supplier 
            FROM ITEM_SUMBER_DAYA ISD, DAFTAR_ITEM DI
            WHERE DI.kode_item_sumber_daya = ISD.kode and no_transaksi_sumber_daya = {idPesanan};
            """)
            row = cursor.fetchall()
            allSupplier = []
            for i in row:
                allSupplier.append(i[0])

        # Mengambil nama item berdasarkan kode
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT nama,harga_satuan,username_supplier
            FROM item_sumber_daya
            WHERE kode='{request.POST['kode']}'
            """)
            row = cursor.fetchall()
            
            pesananUpdate.append(tuple((len(pesananUpdate)+1,row[0][0],row[0][1],request.POST['jumlahBarang'],row[0][2])))
        context = {
            "id":idPesanan,
            "supp":request.POST['supplier'],
            "kodeBarang":kodeBarang,
            "allSupplier": allSupplier,
            "pesanan_query": pesananUpdate
        }
    # Untuk delete
    elif request.method=="POST" and request.POST['tombol'] != "simpan" and request.POST['tombol'] != "tambah" and request.POST['tombol'] != "choose":
        index = int(request.POST['tombol'])-1
        del pesananUpdate[index]

        for i in range(index,len(pesananUpdate)):
            dataBaru = (str(i+1),pesananUpdate[i][1],pesananUpdate[i][2],pesananUpdate[i][3])
            pesananUpdate[i] = dataBaru
        
        # Mengambil seluruh kode barang yg dimiliki supplier
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode
            FROM ITEM_SUMBER_DAYA
            WHERE username_supplier='{request.POST["supplier"]}'
            """)
            row = cursor.fetchall()
            kodeBarang = []
            for i in row:
                kodeBarang.append(i[0])

        # Mengambil seluruh username yang menyediakan item sumber daya
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT ISD.username_supplier 
            FROM ITEM_SUMBER_DAYA ISD, DAFTAR_ITEM DI
            WHERE DI.kode_item_sumber_daya = ISD.kode and no_transaksi_sumber_daya = {idPesanan};
            """)
            row = cursor.fetchall()
            allSupplier = []
            for i in row:
                allSupplier.append(i[0])

        context = {
            "id":idPesanan,
            "supp":request.POST['supplier'],
            "kodeBarang":kodeBarang,
            "allSupplier": allSupplier,
            "pesanan_query": pesananUpdate
        }
    elif request.method == "POST" and request.POST['tombol'] == "simpan" :
        # Update tanggal transaksi_sumber_daya
        with connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE TRANSAKSI_SUMBER_DAYA 
            SET tanggal = '{date.today()}' 
            WHERE nomor = {idPesanan};
            """)

        # Get MAX no urut dari pesanan 
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT MAX(no_urut) 
            FROM DAFTAR_ITEM WHERE 
            no_transaksi_sumber_daya = {idPesanan};
            """)
            row = cursor.fetchall()
            maxNoUrut = row[0][0]
        # Insert Daftar_Item
        for i in pesananUpdate:
            maxNoUrut+=1
            with connection.cursor() as cursor:
                cursor.execute(f"""
                SELECT kode 
                FROM ITEM_SUMBER_DAYA
                WHERE nama='{i[1]}'
                """)
                kode = cursor.fetchall()
            with connection.cursor() as cursor:
                cursor.execute(f"""
                INSERT INTO DAFTAR_ITEM VALUES
                ({idPesanan},{maxNoUrut},{i[3]},{kode[0][0]},0.0,0.0)
                """)
        pesananUpdate.clear()
        return redirect("trigger3:ReadPesananSumberDaya")
    else:        
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT ISD.username_supplier 
            FROM ITEM_SUMBER_DAYA ISD, DAFTAR_ITEM DI
            WHERE DI.kode_item_sumber_daya = ISD.kode and no_transaksi_sumber_daya = {idPesanan};
            """)
            row = cursor.fetchall()
            allSupplier = []
            for i in row:
                allSupplier.append(i[0])
        context = {
            "id":idPesanan,
            "allSupplier":allSupplier
        }
    return render(request,'trigger3/UpdatePesanan.html',context)


def SupplierReadPesanan(request):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT DISTINCT PSD.nomor_pesanan, PSD.username_admin_satgas, RSP.tanggal,TSD.total_berat,TSD.total_item,PSD.total_harga
        FROM PESANAN_SUMBER_DAYA PSD, ITEM_SUMBER_DAYA ISD, DAFTAR_ITEM DI, RIWAYAT_STATUS_PESANAN RSP,
        TRANSAKSI_SUMBER_DAYA TSD
        WHERE 
        ISD.kode = DI.kode_item_sumber_daya AND 
        DI.no_transaksi_sumber_daya = PSD.nomor_pesanan AND 
        DI.no_transaksi_sumber_daya = TSD.nomor AND
        RSP.no_pesanan = PSD.nomor_pesanan AND 
        ISD.username_supplier = RSP.username_supplier AND 
        ISD.username_supplier = '{request.session["username"]}';
        """)
        dataPertama = cursor.fetchall()
    dataStatus = []
    for i in dataPertama:
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode_status_pesanan 
            FROM RIWAYAT_STATUS_PESANAN
            WHERE username_supplier='{request.session["username"]}' and no_pesanan = '{i[0]}';
            """)
            row = cursor.fetchall()
            dataStatus.append(row[-1][0])
    result = []
    for i in range(len(dataPertama)):
        hasil = (dataPertama[i][0],dataPertama[i][1],dataPertama[i][2],dataPertama[i][3],dataPertama[i][4],dataPertama[i][5],dataStatus[i])
        result.append(hasil)
    context = {
        "result":result,
        "dataStatus":dataStatus
    }

    if request.method == "POST":
        perintah = request.POST['tombol'].split(" ")
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT username_supplier 
            FROM RIWAYAT_STATUS_PESANAN 
            WHERE no_pesanan = {perintah[1]};
            """)
            dataSupplier = cursor.fetchall()
        if perintah[0] == "proses":
            for i in dataSupplier:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                    INSERT INTO RIWAYAT_STATUS_PESANAN VALUES
                    ('PRO-SUP','{perintah[1]}','{i[0]}','{date.today()}');
                    """)
        elif perintah[0] == "reject":
            for i in dataSupplier:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                    INSERT INTO RIWAYAT_STATUS_PESANAN VALUES
                    ('REJ-SUP','{perintah[1]}','{i[0]}','{date.today()}');
                    """)
        elif perintah[0] == "selesai":
            for i in dataSupplier:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                    INSERT INTO RIWAYAT_STATUS_PESANAN VALUES
                    ('FIN-SUP','{perintah[1]}','{i[0]}','{date.today()}');
                    """)
        elif perintah[0] == "masalah":
            for i in dataSupplier:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                    INSERT INTO RIWAYAT_STATUS_PESANAN VALUES
                    ('MAS-SUP','{perintah[1]}','{i[0]}','{date.today()}');
                    """)
        return redirect("trigger3:SupplierReadPesanan")
    return render(request,"trigger3/SupplierReadPesanan.html",context)

def detailPesananSupplier(request,idPesanan):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT TSD.tanggal, PSD.total_harga,DI.no_urut, DI.kode_item_sumber_daya, 
        DI.jumlah_item, PSD.username_admin_satgas
        FROM TRANSAKSI_SUMBER_DAYA TSD, DAFTAR_ITEM DI, PESANAN_SUMBER_DAYA PSD
        WHERE PSD.nomor_pesanan = TSD.nomor and TSD.nomor = DI.no_transaksi_sumber_daya AND
        PSD.nomor_pesanan={idPesanan};
        """)
        dataPertama = cursor.fetchall()

    dataKedua = []
    for i in dataPertama:
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT ISD.username_supplier,ISD.nama, ISD.harga_satuan
            FROM ITEM_SUMBER_DAYA ISD, DAFTAR_ITEM DI
            WHERE DI.kode_item_sumber_daya = ISD.kode and DI.kode_item_sumber_daya='{i[3]}';
            """)
            result = cursor.fetchall()
            dataKedua.append(result[0])
    result =[]
    for i in range(len(dataPertama)):
        setup = (dataPertama[i][0],dataPertama[i][2],dataKedua[i][1],dataKedua[i][0],dataKedua[i][2],dataPertama[i][4],dataPertama[i][1])
        result.append(setup)
    context = {
        "admin_satgas":dataPertama[0][5],
        "idPesanan":idPesanan,
        "result":result
    }
    return render(request, 'trigger3/DetailPesananSupplier.html',context)

def riwayatStatusSupplier(request,idPesanan):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT RSP.kode_status_pesanan ,SP.nama,RSP.username_supplier,RSP.tanggal
        FROM RIWAYAT_STATUS_PESANAN RSP, STATUS_PESANAN SP
        WHERE RSP.kode_status_pesanan = SP.kode and RSP.no_pesanan={idPesanan} 
        and RSP.username_supplier = '{request.session["username"]}';
        """)
        row = cursor.fetchall()
    timeSort = []
    for i in reversed(row):
        timeSort.append(i)
    context = {
        "result":timeSort,
        "id":idPesanan
    }
    return render(request,'trigger3/RiwayatStatusSupplier.html',context)

def createStockFaskes(request):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT DISTINCT kode_faskes FROM STOK_FASKES;
        """)
        kodeFaskes = cursor.fetchall()
    context = {
        "kodeFaskes":kodeFaskes
    }

    if request.method == "POST" and request.POST['tombol'] == "choose" :
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT DISTINCT kode 
            FROM ITEM_SUMBER_DAYA;
            """)
            kodeItem = cursor.fetchall()
        context = {
        "kodeFaskes":kodeFaskes,
        "kodeFaskesPilihan":request.POST['kode'],
        "kodeItem":kodeItem
        }
    elif request.method == "POST" and request.POST['tombol'] == "choose2" :
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT nama
            FROM item_sumber_daya
            WHERE kode='{request.POST['kodeItem']}';
            """)
            namaItem = cursor.fetchall()
        context = {
        "kodeItem2": request.POST['kodeItem'],
        "kodeFaskes":kodeFaskes,
        "namaItem":namaItem,
        "kodeFaskesPilihan": request.POST['kodeFaskesPilihan'],
        }
    elif request.method == "POST" and request.POST['tombol'] == "simpan":
        kodeFaskes = request.POST['kodeFaskesPilihan']
        kodeItem = request.POST['kodeItem2']
        jumlahBarang = request.POST['jumlahBarang']
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT * from STOK_FASKES
            WHERE kode_faskes = '{kodeFaskes}' and kode_item_sumber_daya='{kodeItem}';
            """)
            result = cursor.fetchall()
        if len(result) == 0:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                INSERT INTO STOK_FASKES VALUES
                ('{kodeFaskes}','{kodeItem}',{jumlahBarang})
                """)
        else:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                SELECT jumlah from STOK_FASKES
                WHERE kode_faskes = '{kodeFaskes}' and kode_item_sumber_daya='{kodeItem}';
                """)
                jumlahAwal = cursor.fetchall()
            jumlahAkhir = int(jumlahBarang) + jumlahAwal[0][0]
            with connection.cursor() as cursor:
                cursor.execute(f"""
                UPDATE STOK_FASKES
                set jumlah = {jumlahAkhir}
                WHERE kode_faskes = '{kodeFaskes}' and kode_item_sumber_daya='{kodeItem}';
                """)
        return redirect("trigger3:ListStockFaskes")
    return render(request,'trigger3/CreateStockFaskes.html',context)

def listStockFaskes(request):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT SF.kode_faskes, TF.nama_tipe, ISD.nama, SF.jumlah
        FROM STOK_FASKES SF, FASKES F, TIPE_FASKES TF, ITEM_SUMBER_DAYA ISD
        WHERE SF.kode_faskes = F.kode_faskes_nasional and F.kode_tipe_faskes = TF.kode
        and SF.kode_item_sumber_daya = ISD.kode;
        """)
        result = cursor.fetchall()
    context = {
        "result":result
    }
    if request.method == "POST":
        result = request.POST['tombol']
        key1 = result.split(' ',1)[0]
        key2 = result.split(' ',1)[1]
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT kode 
            FROM item_sumber_daya 
            WHERE nama = '{key2}';
            """)
            kodeItem = cursor.fetchall()
        kodeItem = kodeItem[0][0]
        with connection.cursor() as cursor:
            cursor.execute(f"""
            DELETE FROM stok_faskes
            WHERE kode_faskes='{key1}' and kode_item_sumber_daya='{kodeItem}'
            """)
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT SF.kode_faskes, TF.nama_tipe, ISD.nama, SF.jumlah
            FROM STOK_FASKES SF, FASKES F, TIPE_FASKES TF, ITEM_SUMBER_DAYA ISD
            WHERE SF.kode_faskes = F.kode_faskes_nasional and F.kode_tipe_faskes = TF.kode
            and SF.kode_item_sumber_daya = ISD.kode;
            """)
            row = cursor.fetchall()
        context = {
            "result":row
        }
    return render(request,'trigger3/ListStockFakses.html',context)

def updateStockFaskes(request,kodeFaskes,namaFaskes,namaItem):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT kode 
        FROM item_sumber_daya 
        WHERE nama = '{namaItem}';
        """)
        kodeItem = cursor.fetchall()
    kodeItem = kodeItem[0][0]
    context = {
        "kodeFaskes":kodeFaskes,
        "namaFaskes":namaFaskes,
        "kodeItem":kodeItem,
        "namaItem":namaItem
    }

    if request.method == "POST":
        jumlahBarang = request.POST['jumlahBarang']
        with connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE STOK_FASKES
            set jumlah = {jumlahBarang}
            WHERE kode_faskes = '{kodeFaskes}' and kode_item_sumber_daya='{kodeItem}';
            """)
        return redirect("trigger3:ListStockFaskes")
    return render(request,'trigger3/UpdateStockFaskes.html',context)

def ListStockFaskesPetugas(request):
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT SF.kode_faskes, TF.nama_tipe, ISD.nama, SF.jumlah
        FROM STOK_FASKES SF, FASKES F, TIPE_FASKES TF, ITEM_SUMBER_DAYA ISD
        WHERE F.username_petugas = '{request.session["username"]}' and F.kode_faskes_nasional = SF.kode_faskes
        and F.kode_tipe_faskes = TF.kode and SF.kode_item_sumber_daya = ISD.kode;
        """)
        result = cursor.fetchall()
    context = {
        "result":result
    }
    return render(request,'trigger3/ListStockFaskesPetugas.html',context)