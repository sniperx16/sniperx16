package com.firma.calisanrehberi

object CsvImport {
    /** Tırnaklı alanları, ; , veya TAB ayracını ve alan içi satır sonlarını destekler. */
    fun parse(text0: String): List<List<String>> {
        val text = text0.removePrefix("﻿")
        val firstLine = text.lineSequence().firstOrNull() ?: return emptyList()
        val delim = listOf(';', ',', '\t').maxByOrNull { d -> firstLine.count { it == d } } ?: ';'
        val rows = ArrayList<List<String>>()
        var row = ArrayList<String>()
        val f = StringBuilder()
        var inQ = false
        var i = 0
        fun endField() { row.add(f.toString().trim()); f.setLength(0) }
        fun endRow() { endField(); if (row.any { it.isNotEmpty() }) rows.add(row); row = ArrayList() }
        while (i < text.length) {
            val c = text[i]
            when {
                inQ && c == '"' && i + 1 < text.length && text[i + 1] == '"' -> { f.append('"'); i++ }
                c == '"' -> inQ = !inQ
                !inQ && c == delim -> endField()
                !inQ && c == '\n' -> endRow()
                !inQ && c == '\r' -> {}
                else -> f.append(c)
            }
            i++
        }
        if (f.isNotEmpty() || row.isNotEmpty()) endRow()
        return rows
    }

    private val aliases = mapOf(
        "ad" to listOf("adsoyad", "adisoyadi", "isimsoyisim", "isim", "personel", "calisan", "ad"),
        "soyad" to listOf("soyad", "soyadi", "soyisim"),
        "tc" to listOf("tc", "tcno", "tckn", "tckimlikno", "kimlikno", "tcnumarasi"),
        "tel" to listOf("telefon", "tel", "cep", "gsm", "ceptelefonu", "telefonno", "cepno"),
        "adres" to listOf("adres", "ikametadresi", "evadresi"),
        "birim" to listOf("birim", "departman", "bolum", "sube", "proje", "sirket"),
        "gorev" to listOf("gorev", "unvan", "pozisyon", "meslek"),
        "eposta" to listOf("eposta", "email", "mail", "epostaadresi"),
        "not" to listOf("not", "notlar", "aciklama")
    )

    fun toEmployees(rows: List<List<String>>): List<Employee> {
        if (rows.size < 2) return emptyList()
        val head = rows[0].map { norm(it).filter { ch -> ch.isLetterOrDigit() } }
        fun idx(key: String): Int {
            val al = aliases[key]!!
            for (a in al) { val i = head.indexOf(a); if (i >= 0) return i }
            return -1
        }
        val iAd = idx("ad"); val iSoy = idx("soyad"); val iTc = idx("tc"); val iTel = idx("tel")
        val iAdr = idx("adres"); val iBir = idx("birim"); val iGor = idx("gorev")
        val iEp = idx("eposta"); val iNot = idx("not")
        fun g(r: List<String>, i: Int) = if (i in r.indices) r[i] else ""
        return rows.drop(1).mapNotNull { r ->
            val ad = (g(r, iAd) + (if (iSoy >= 0 && iSoy != iAd) " " + g(r, iSoy) else "")).trim()
            if (ad.isEmpty() && g(r, iTc).isEmpty()) null
            else Employee(0, ad, g(r, iTc), g(r, iTel), g(r, iAdr), g(r, iBir), g(r, iGor), g(r, iEp), g(r, iNot))
        }
    }
}
