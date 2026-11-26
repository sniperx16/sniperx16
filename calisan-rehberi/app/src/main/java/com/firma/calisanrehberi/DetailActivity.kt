package com.firma.calisanrehberi

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
        val e = Db(this).get(intent.getLongExtra("id", -1)) ?: run { finish(); return }
        title = e.adSoyad
        val pad = (16 * resources.displayMetrics.density).toInt()
        val col = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(pad, pad, pad, pad) }

        fun field(label: String, value: String) {
            if (value.isEmpty()) return
            col.addView(TextView(this).apply { text = label; textSize = 12f; alpha = 0.6f; setPadding(0, pad / 2, 0, 0) })
            col.addView(TextView(this).apply {
                text = value; textSize = 17f; setTextIsSelectable(true)
                setOnLongClickListener {
                    (getSystemService(CLIPBOARD_SERVICE) as ClipboardManager).setPrimaryClip(ClipData.newPlainText(label, value))
                    Toast.makeText(this@DetailActivity, "$label kopyalandı", Toast.LENGTH_SHORT).show(); true
                }
            })
        }
        field("Ad Soyad", e.adSoyad); field("TC Kimlik No", e.tc); field("Telefon", e.telefon)
        field("Adres", e.adres); field("Birim", e.birim); field("Görev", e.gorev)
        field("E-posta", e.eposta); field("Not", e.not)

        fun button(text: String, show: Boolean, action: () -> Unit) {
            if (!show) return
            col.addView(Button(this).apply { this.text = text; setOnClickListener { action() } })
        }
        fun open(i: Intent) = try { startActivity(i) } catch (x: Exception) {
            Toast.makeText(this, "Uygun uygulama bulunamadı", Toast.LENGTH_SHORT).show()
        }
        val tel = e.telefon.filter { it.isDigit() || it == '+' }
        col.addView(View(this).apply { minimumHeight = pad })
        button("Ara", tel.isNotEmpty()) { open(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$tel"))) }
        button("SMS gönder", tel.isNotEmpty()) { open(Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:$tel"))) }
        button("Haritada göster", e.adres.isNotEmpty()) {
            open(Intent(Intent.ACTION_VIEW, Uri.parse("geo:0,0?q=" + Uri.encode(e.adres))))
        }
        button("E-posta gönder", e.eposta.isNotEmpty()) { open(Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:${e.eposta}"))) }
        setContentView(ScrollView(this).apply { addView(col) })
    }
}
