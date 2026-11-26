package com.firma.calisanrehberi

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.Menu
import android.view.MenuItem
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {
    private lateinit var db: Db
    private lateinit var adapter: Adapter
    private lateinit var info: TextView
    private lateinit var search: EditText
    private var unlocked = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Ekran görüntüsü ve son uygulamalar önizlemesini engelle (kişisel veri).
        window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
        setContentView(R.layout.activity_main)
        db = Db(this)
        info = findViewById(R.id.info)
        search = findViewById(R.id.search)
        adapter = Adapter { e -> startActivity(Intent(this, DetailActivity::class.java).putExtra("id", e.id)) }
        findViewById<RecyclerView>(R.id.list).apply {
            layoutManager = LinearLayoutManager(this@MainActivity); adapter = this@MainActivity.adapter
        }
        search.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { refresh() }
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
        })
        findViewById<RecyclerView>(R.id.list).visibility = android.view.View.INVISIBLE
    }

    override fun onStart() {
        super.onStart()
        if (!unlocked) authenticate() else refresh()
    }

    override fun onStop() { super.onStop(); unlocked = false; findViewById<RecyclerView>(R.id.list).visibility = android.view.View.INVISIBLE }

    private fun authenticate() {
        val auth = BiometricManager.Authenticators.BIOMETRIC_WEAK or BiometricManager.Authenticators.DEVICE_CREDENTIAL
        if (BiometricManager.from(this).canAuthenticate(auth) != BiometricManager.BIOMETRIC_SUCCESS) {
            Toast.makeText(this, "Uyarı: telefonda ekran kilidi yok. Verileri korumak için kilit ayarlayın.", Toast.LENGTH_LONG).show()
            unlock(); return
        }
        val prompt = BiometricPrompt(this, ContextCompat.getMainExecutor(this),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(r: BiometricPrompt.AuthenticationResult) { unlock() }
                override fun onAuthenticationError(code: Int, msg: CharSequence) { finish() }
            })
        prompt.authenticate(
            BiometricPrompt.PromptInfo.Builder().setTitle("Çalışan Rehberi")
                .setSubtitle("Devam etmek için kimliğinizi doğrulayın").setAllowedAuthenticators(auth).build()
        )
    }

    private fun unlock() {
        unlocked = true
        findViewById<RecyclerView>(R.id.list).visibility = android.view.View.VISIBLE
        refresh()
    }

    private fun refresh() {
        val total = db.count()
        val res = db.search(search.text.toString())
        adapter.submit(res)
        info.text = if (total == 0) "Kayıt yok. Menüden “CSV içe aktar” ile çalışan listesini yükleyin."
        else "${res.size} sonuç (toplam $total kayıt)"
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean { menuInflater.inflate(R.menu.main, menu); return true }

    private val picker = registerForActivityResult(androidx.activity.result.contract.ActivityResultContracts.OpenDocument()) { uri ->
        if (uri == null) return@registerForActivityResult
        thread {
            try {
                val text = contentResolver.openInputStream(uri)!!.use { it.readBytes() }.toString(Charsets.UTF_8)
                val list = CsvImport.toEmployees(CsvImport.parse(text))
                db.replaceAll(list)
                runOnUiThread {
                    Toast.makeText(this, "${list.size} kayıt yüklendi", Toast.LENGTH_LONG).show(); refresh()
                }
            } catch (e: Exception) {
                runOnUiThread { Toast.makeText(this, "Hata: ${e.message}", Toast.LENGTH_LONG).show() }
            }
        }
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.m_import -> AlertDialog.Builder(this)
                .setMessage("Mevcut tüm kayıtlar silinip seçeceğiniz CSV dosyasındaki liste yüklenecek. Devam edilsin mi?")
                .setPositiveButton("Devam") { _, _ -> picker.launch(arrayOf("*/*")) }
                .setNegativeButton("İptal", null).show()
            R.id.m_clear -> AlertDialog.Builder(this).setMessage("Telefondaki tüm çalışan verisi silinsin mi?")
                .setPositiveButton("Sil") { _, _ -> db.clear(); refresh() }
                .setNegativeButton("İptal", null).show()
        }
        return true
    }

    private class Adapter(val onClick: (Employee) -> Unit) : RecyclerView.Adapter<Adapter.VH>() {
        private var items: List<Employee> = emptyList()
        fun submit(l: List<Employee>) { items = l; notifyDataSetChanged() }
        class VH(v: android.view.View) : RecyclerView.ViewHolder(v) {
            val name: TextView = v.findViewById(R.id.name); val sub: TextView = v.findViewById(R.id.sub)
        }
        override fun onCreateViewHolder(p: ViewGroup, t: Int) =
            VH(LayoutInflater.from(p.context).inflate(R.layout.item_employee, p, false))
        override fun getItemCount() = items.size
        override fun onBindViewHolder(h: VH, i: Int) {
            val e = items[i]
            h.name.text = e.adSoyad.ifEmpty { "(isimsiz)" }
            h.sub.text = listOf(e.birim, e.telefon).filter { it.isNotEmpty() }.joinToString("  •  ")
            h.itemView.setOnClickListener { onClick(e) }
        }
    }
}
