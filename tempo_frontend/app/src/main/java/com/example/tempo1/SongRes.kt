package com.example.tempo1

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class SongRes (
    val tracks: List<Song>,
)