//
//  Top10View.swift
//  spotipie
//
//  Created by Sudhip Nashi on 27/07/24.
//

import SwiftUI

struct Top10SongView: View {
    @State var globalData: GlobalData?
    
    var body: some View {
        NavigationStack {
            List {
                ForEach(globalData?.ten_most_played_tracks ?? [], id: \.id) { song in
                    NavigationLink {
                        SongDetail(song: Song(id: song.id))
                    } label: {
                        Top10Cell(name: song.name, image_url: song.cover_image_url, play_count: song.play_count)
                    }
                }
                .navigationTitle("Top 10 Songs")
            }
        }
    }
}
