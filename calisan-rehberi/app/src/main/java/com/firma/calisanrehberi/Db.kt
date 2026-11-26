package com.firma.calisanrehberi

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.util.Locale

data class Employee(
    val id: Long, val adSoyad: String, val tc: String, val telefon: String,
    val adres: String, val birim: String, val gorev: String, val eposta: String, val not: String
)

/** Türkçe karakterleri ve büyük/küçük harf farkını eleyerek karşılaştırma metni üretir. */
fun norm(s: String): String = s.lowercase(Locale("tr"))
    .replace('ç', 'c').replace('ş', 's').replace('ğ', 'g')
    .replace('ı', 'i').replace('ö', 'o').replace('ü', 'u')

class Db(ctx: Context) : SQLiteOpenHelper(ctx, "calisanlar.db", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """CREATE TABLE emp(id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, tc TEXT, tel TEXT,
               adres TEXT, birim TEXT, gorev TEXT, eposta TEXT, notu TEXT, arama TEXT)"""
        )
    }
    override fun onUpgrade(db: SQLiteDatabase, o: Int, n: Int) {}

    fun replaceAll(rows: List<Employee>) {
        val db = writableDatabase
        db.beginTransaction()
        try {
            db.delete("emp", null, null)
            for (e in rows) {
                val cv = ContentValues().apply {
                    put("ad", e.adSoyad); put("tc", e.tc); put("tel", e.telefon)
                    put("adres", e.adres); put("birim", e.birim); put("gorev", e.gorev)
                    put("eposta", e.eposta); put("notu", e.not)
                    put("arama", norm("${e.adSoyad} ${e.tc} ${e.telefon.filter { it.isDigit() }} ${e.birim} ${e.gorev}"))
                }
                db.insert("emp", null, cv)
            }
            db.setTransactionSuccessful()
        } finally { db.endTransaction() }
    }

    fun clear() { writableDatabase.delete("emp", null, null) }

    fun count(): Int = readableDatabase.rawQuery("SELECT COUNT(*) FROM emp", null).use { it.moveToFirst(); it.getInt(0) }

    fun search(q: String, limit: Int = 500): List<Employee> {
        val terms = norm(q).split(' ').filter { it.isNotBlank() }
        val where = terms.joinToString(" AND ") { "arama LIKE ?" }.ifEmpty { "1" }
        val args = terms.map { "%$it%" }.toTypedArray()
        val out = ArrayList<Employee>()
        readableDatabase.rawQuery(
            "SELECT id,ad,tc,tel,adres,birim,gorev,eposta,notu FROM emp WHERE $where ORDER BY ad COLLATE NOCASE LIMIT $limit", args
        ).use { c ->
            while (c.moveToNext()) out.add(
                Employee(c.getLong(0), c.getString(1) ?: "", c.getString(2) ?: "", c.getString(3) ?: "",
                    c.getString(4) ?: "", c.getString(5) ?: "", c.getString(6) ?: "",
                    c.getString(7) ?: "", c.getString(8) ?: "")
            )
        }
        return out
    }

    fun get(id: Long): Employee? = readableDatabase.rawQuery(
        "SELECT id,ad,tc,tel,adres,birim,gorev,eposta,notu FROM emp WHERE id=?", arrayOf(id.toString())
    ).use { c ->
        if (!c.moveToFirst()) null else Employee(c.getLong(0), c.getString(1) ?: "", c.getString(2) ?: "",
            c.getString(3) ?: "", c.getString(4) ?: "", c.getString(5) ?: "", c.getString(6) ?: "",
            c.getString(7) ?: "", c.getString(8) ?: "")
    }
}
