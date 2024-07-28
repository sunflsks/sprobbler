//
//  Top10View.swift
//  spotipie
//
//  Created by Sudhip Nashi on 27/07/24.
//

import SwiftUI

struct Top10AlbumView: View {
    @State var globalData: GlobalData?
    
    var body: some View {
        NavigationStack {
            List {
                ForEach(globalData?.ten_most_played_albums ?? [], id: \.id) { album in
                    NavigationLink {
                        AlbumDetailView(album: Album(id: album.id))
                    } label: {
                        GenericCell(name: album.name, image_url: album.cover_image_url, play_count: album.play_count)
                    }
                }
                .navigationTitle("Top 10 Albums")
            }
        }
    }
}
