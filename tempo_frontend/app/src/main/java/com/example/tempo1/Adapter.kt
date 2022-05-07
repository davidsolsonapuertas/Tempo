package com.example.tempo1

import android.content.Intent
import android.net.Uri
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.TextView
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import kotlinx.coroutines.withContext
import java.net.URI

class Adapter(val myDataset: ArrayList<Song>, val callbackInterface: CallbackInterface) : RecyclerView.Adapter<Adapter.MyViewHolder>() {

    interface CallbackInterface {
        fun onClick(position: Int, songInfo: Song)
    }

    // Define a custom view holder for each item in the list
    class MyViewHolder (view : View, callbackInterface: CallbackInterface) : RecyclerView.ViewHolder(view) {
        // Add additional variables and values here
        val layout: ConstraintLayout = view.findViewById(R.id.layout)
        val song: TextView = view.findViewById(R.id.song)
        val length: TextView = view.findViewById(R.id.length)
        val artist: TextView = view.findViewById(R.id.artist)
        val albumcover: ImageView = view.findViewById(R.id.albumcover)
        val playButton: ImageButton = view.findViewById(R.id.playButton)
    }

    // Create new views (invoked by the layout manager)
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int)
            : Adapter.MyViewHolder {
        // Creates the new view for each cell. Instead of a simple TextView,
        // this can be a CardView or a ViewGroup
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.reycler_item, parent, false) as ConstraintLayout
        return MyViewHolder(view, callbackInterface)
    }

    // Replace the contents of a view (invoked by the layout manager)
    override fun onBindViewHolder(holder: Adapter.MyViewHolder, position: Int) {
        holder.song.text = myDataset[position].name
        holder.length.text = myDataset[position].name
        holder.artist.text = myDataset[position].artists.joinToString(separator = ", ") {
            el -> el.name
        }
        Glide.with(holder.layout).load(myDataset[position].album.images[0].url).into(holder.albumcover);
        holder.layout.setOnClickListener {
            callbackInterface.onClick(position, myDataset[position])
        }

        holder.playButton.setOnClickListener() {
            val i = Intent(Intent.ACTION_VIEW, Uri.parse(myDataset[position].href))
            it.getContext().startActivity(i)
        }
    }

    // Return the size of your dataset (invoked by the layout manager)
    override fun getItemCount(): Int{
        return myDataset.size
    }
}