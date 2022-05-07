package com.example.tempo1

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
class RequestPlaylist (
    val hours: Int,
    val minutes: Int,
)