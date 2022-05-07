package com.example.tempo1

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class Images (
    val url: String
        )

@JsonClass(generateAdapter = true)
data class Album (
    val images: List<Images>
        )

@JsonClass(generateAdapter = true)
data class Artist (
    val name: String
)

@JsonClass(generateAdapter = true)
data class Song (
    val name: String,
    val duration_ms: Int,
    val artists: List<Artist>,
    val href: String,
    val album: Album
)