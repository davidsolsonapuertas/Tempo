package com.example.tempo1

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.squareup.moshi.JsonAdapter
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException


class GeneratedPlaylistActivity : AppCompatActivity(), Adapter.CallbackInterface {
    private val client = OkHttpClient()
    private val moshi = Moshi.Builder().addLast(KotlinJsonAdapterFactory()).build()
    private val songDataJsonAdapter : JsonAdapter<SongRes> = moshi.adapter(SongRes::class.java)
    private val reqDataJsonAdapter : JsonAdapter<RequestPlaylist> = moshi.adapter(RequestPlaylist::class.java)
    private val songListType = Types.newParameterizedType(List::class.java, Song::class.java)
    private val songs: MutableList<Song> = mutableListOf()
    lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_generated_playlist)

        var mins = getIntent().extras?.getString("mins")
        var hours = getIntent().extras?.getString("hours")
        var token = getIntent().extras?.getString("token")!!
        recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.setHasFixedSize(true)

        val layoutManager = LinearLayoutManager(this@GeneratedPlaylistActivity)
        recyclerView.layoutManager = layoutManager

        requestPlaylist(1, 20, token)

        val submitButton = findViewById<Button>(R.id.createPlaylistButton)
        val regenerateButton = findViewById<Button>(R.id.regeneratePlaylistButton)
        val saveButton = findViewById<Button>(R.id.savePlaylistButton)

        saveButton.setOnClickListener(){
            val intent = Intent(this, FavoritePlaylistActivity::class.java)
            val playlist = PlaylistDetails("Title", "Length", R.drawable.musicnote, songs as ArrayList<Song>)
            Singleton.addPlaylist(playlist)

            startActivity(intent)
        }

        regenerateButton.setOnClickListener(){
            requestPlaylist(1, 20, token)
        }
    }

    override fun onClick(position: Int, songInfo: Song) {
        TODO("Not yet implemented")
    }

    private fun requestPlaylist(hours: Int, minutes: Int, token: String) {
        val body = RequestPlaylist(hours, minutes)

        val request = Request.Builder().url(BASE_URL + "tempo/playlist/")
            .post(reqDataJsonAdapter.toJson(body).toRequestBody(("application/json; charset=utf-8").toMediaType()))
            .addHeader("Authorization", "Bearer $token")
            .build()

        client.newCall(request).enqueue(object: Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if(!it.isSuccessful) {
                        Log.d("Populate unsuccessful", response.toString())
                    } else {
                        val songData = songDataJsonAdapter.fromJson(response.body?.source())!!
                        val songList = songData.tracks

                        for(song in songList) {
                            songs.add(song)
                        }
                        runBlocking {
                            withContext(Dispatchers.Main) {
                                responseReady(songs)
                            }
                        }
                    }
                }
            }
        })
    }

    private fun responseReady(songs: List<Song>) {

        var position = getIntent().extras?.getInt("Position")

        val adapter = Adapter(songs as ArrayList<Song>,this)
        recyclerView.adapter = adapter
    }
}
