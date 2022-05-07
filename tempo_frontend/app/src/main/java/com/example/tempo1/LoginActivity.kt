package com.example.tempo1

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.spotify.sdk.android.auth.AuthorizationClient
import com.spotify.sdk.android.auth.AuthorizationRequest
import com.spotify.sdk.android.auth.AuthorizationResponse
import com.spotify.sdk.android.auth.LoginActivity.REQUEST_CODE


class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val REQUEST_CODE = 1138
        val REDIRECT_URI = "tempo://callback"
        val CLIENT_ID = "719abab79c634ef9a41b1cadbd6ceb45"

        val builder =
            AuthorizationRequest.Builder(CLIENT_ID, AuthorizationResponse.Type.TOKEN, REDIRECT_URI)

        builder.setScopes(arrayOf("user-read-recently-played", "user-top-read", "user-read-playback-state"))
        val request = builder.build()

        AuthorizationClient.openLoginActivity(this, REQUEST_CODE, request)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val response = AuthorizationClient.getResponse(resultCode, data)

        if (requestCode == REQUEST_CODE) {

            when (response.type) {
                AuthorizationResponse.Type.TOKEN -> {
                    val intent = Intent(this, GetPlaylistActivity::class.java)
                    intent.putExtra("token", response.accessToken)
                    Log.d("StatusToken: ", response.accessToken)

                    startActivity(intent)
                }
                AuthorizationResponse.Type.ERROR -> {
                }
                else -> {
                }
            }
        }
    }
}