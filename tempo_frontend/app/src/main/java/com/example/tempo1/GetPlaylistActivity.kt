package com.example.tempo1

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import com.squareup.moshi.JsonAdapter
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody


const val BASE_URL = "http://34.130.140.246/"

class GetPlaylistActivity : AppCompatActivity() {
    private val moshi = Moshi.Builder().addLast(KotlinJsonAdapterFactory()).build()
    private val songListType = Types.newParameterizedType(List::class.java, Song::class.java)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_get_playlist)

        val hoursEdit = findViewById<EditText>(R.id.hoursBox) as EditText
        val minsEdit = findViewById<EditText>(R.id.minutesBox) as EditText

        var submitButton = findViewById<Button>(R.id.createPlaylistButton)
        var hours = hoursEdit.text.toString()
        var mins = minsEdit.text.toString()
        var token = getIntent().extras?.getString("token")

        submitButton.setOnClickListener() {
            intent = Intent(this, GeneratedPlaylistActivity::class.java)
            intent.putExtra("mins", mins)
            intent.putExtra("hours", hours)
            intent.putExtra("token", token)

            startActivity(intent)
        }
    }
}