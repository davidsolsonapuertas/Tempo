package com.example.tempo1

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class FavoritePlaylistActivity : AppCompatActivity(), Adapter2.CallbackInterface {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_favorite_playlist)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)

        recyclerView.setHasFixedSize(true)

        val layoutManager = LinearLayoutManager(this@FavoritePlaylistActivity)
        recyclerView.layoutManager = layoutManager

        var myDataset = Singleton.playlists

        val adapter = Adapter2(myDataset,this)
        recyclerView.adapter = adapter
    }

    override fun onClick(position: Int, playlistInfo: PlaylistDetails) {
        val intent = Intent(this, GeneratedPlaylistActivity::class.java)

        intent.putExtra("Position", position)

        startActivity(intent)
    }
}