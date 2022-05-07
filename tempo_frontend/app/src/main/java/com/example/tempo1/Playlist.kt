package com.example.tempo1

import com.squareup.moshi.JsonClass

class Playlist private constructor() {
    companion object {
        val playlist = mutableListOf<Song>()
    }
}