package com.example.tempo1

object Singleton {

    val playlists: ArrayList<PlaylistDetails>

    init{
        playlists = ArrayList<PlaylistDetails>()
    }

    fun addPlaylist(variable: PlaylistDetails){
        playlists.add(variable)
    }

}