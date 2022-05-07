package com.example.tempo1

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.recyclerview.widget.RecyclerView

class Adapter2(val myDataset: ArrayList<PlaylistDetails>, val callbackInterface: CallbackInterface) : RecyclerView.Adapter<Adapter2.MyViewHolder>() {

    interface CallbackInterface {
        fun onClick(position: Int, playlistInfo: PlaylistDetails)
    }

    // Define a custom view holder for each item in the list
    class MyViewHolder (view : View, callbackInterface: CallbackInterface) : RecyclerView.ViewHolder(view) {
        // Add additional variables and values here
        val layout: ConstraintLayout = view.findViewById(R.id.layout)
        val title: TextView = view.findViewById(R.id.song)
        val length: TextView = view.findViewById(R.id.length)
        val artist: TextView = view.findViewById(R.id.artist)
        val albumcover: ImageView = view.findViewById(R.id.albumcover)
    }

    // Create new views (invoked by the layout manager)
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int)
            : Adapter2.MyViewHolder {
        // Creates the new view for each cell. Instead of a simple TextView,
        // this can be a CardView or a ViewGroup
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.reycler_item, parent, false) as ConstraintLayout
        return MyViewHolder(view, callbackInterface)
    }

    // Replace the contents of a view (invoked by the layout manager)
    override fun onBindViewHolder(holder: Adapter2.MyViewHolder, position: Int) {
        holder.title.text = myDataset[position].title
        holder.length.text = myDataset[position].length
        holder.artist.text = ""
        holder.albumcover.setImageResource(myDataset[position].cover)
        holder.layout.setOnClickListener {
            callbackInterface.onClick(position, myDataset[position])
        }

    }

    // Return the size of your dataset (invoked by the layout manager)
    override fun getItemCount(): Int{
        return myDataset.size
    }
}